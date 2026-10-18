---
title: Noise Patterns
tags:
  - 描画
---

# Noise Patterns

<strong>AO のサンプル位置を、画素ごとにランダムに回す</strong>と、<strong>規則的な縞（バンディング）が、細かいノイズに変わり、後のぼかしで消えやすくなります</strong>。ノイズの質（白色ノイズ・ブルー ノイズ・インターリーブド グラディエント）で、フィルタの効きと、最終的な見た目が変わります。このページでは、ノイズ パターンの選び方を説明します。

!!! tip "ポイント"
    - サンプルを画素ごとに回転させると、縞がノイズに変わる。
    - 白色ノイズ：単純だが粗い。ブルー ノイズ：高周波に偏り、ぼかしで消えやすい。
    - インターリーブド グラディエント ノイズ：計算で作れ、質が良い。
    - 時間蓄積と組み合わせると、毎フレーム違うパターンで収束が速い。

## なぜ「ノイズの質」が大切なのか

画素ごとにサンプルの向きを変えるとき、向きの決め方（ノイズの種類）によって、後のぼかしでどれだけきれいに消えるかが変わります。

ノイズは、周波数で見ると 2 つの成分に分けられます。<strong>低周波</strong>は「広い範囲で明るい・暗いが偏っている」成分で、<strong>高周波</strong>は「隣り合う画素でバラバラな」成分です。ぼかしは、近くの画素を平均する操作なので、高周波は強く打ち消して減らしますが、低周波はほとんど減らせません。ですから、<strong>ノイズが高周波に偏っているほど、ぼかしできれいに消えます</strong>。

<!-- fig:noise-points:begin -->

<svg class="fig illust motion" data-fig="noise-points" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-noise-points" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ホワイト ノイズは固まりができる。ブルー ノイズは均一に散る</text>
<rect x="60" y="80" width="300" height="260" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="210" y="70" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#64748b">ホワイト ノイズ（独立な乱数）</text>
<circle cx="196.48" cy="224.58" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0472;0.0476;1.0000" values="0;0;1;1"/></circle>
<circle cx="330.48" cy="201.62" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0568;0.0571;1.0000" values="0;0;1;1"/></circle>
<circle cx="212.23" cy="231.32" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0663;0.0667;1.0000" values="0;0;1;1"/></circle>
<circle cx="120.44" cy="212.91" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0758;0.0762;1.0000" values="0;0;1;1"/></circle>
<circle cx="246.89" cy="281.49" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0853;0.0857;1.0000" values="0;0;1;1"/></circle>
<circle cx="94.73" cy="162.03" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0949;0.0952;1.0000" values="0;0;1;1"/></circle>
<circle cx="93.75" cy="285.55" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1044;0.1048;1.0000" values="0;0;1;1"/></circle>
<circle cx="264.94" cy="98.22" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1139;0.1143;1.0000" values="0;0;1;1"/></circle>
<circle cx="346.94" cy="323.4" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1234;0.1238;1.0000" values="0;0;1;1"/></circle>
<circle cx="253.71" cy="238.2" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1330;0.1333;1.0000" values="0;0;1;1"/></circle>
<circle cx="112.73" cy="91.66" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1425;0.1429;1.0000" values="0;0;1;1"/></circle>
<circle cx="218.06" cy="102.53" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1520;0.1524;1.0000" values="0;0;1;1"/></circle>
<circle cx="122.02" cy="147.03" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1615;0.1619;1.0000" values="0;0;1;1"/></circle>
<circle cx="76.54" cy="201.2" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1710;0.1714;1.0000" values="0;0;1;1"/></circle>
<circle cx="193.11" cy="293.55" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1806;0.1810;1.0000" values="0;0;1;1"/></circle>
<circle cx="215.43" cy="244.23" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1901;0.1905;1.0000" values="0;0;1;1"/></circle>
<circle cx="209.94" cy="249.64" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1996;0.2000;1.0000" values="0;0;1;1"/></circle>
<circle cx="197.88" cy="155.87" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2091;0.2095;1.0000" values="0;0;1;1"/></circle>
<circle cx="351.33" cy="330.95" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2187;0.2190;1.0000" values="0;0;1;1"/></circle>
<circle cx="306.62" cy="260.71" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2282;0.2286;1.0000" values="0;0;1;1"/></circle>
<circle cx="157.54" cy="144.04" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2377;0.2381;1.0000" values="0;0;1;1"/></circle>
<circle cx="150.09" cy="105.13" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2472;0.2476;1.0000" values="0;0;1;1"/></circle>
<circle cx="285.63" cy="185.7" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2568;0.2571;1.0000" values="0;0;1;1"/></circle>
<circle cx="308.43" cy="182.31" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2663;0.2667;1.0000" values="0;0;1;1"/></circle>
<circle cx="340.08" cy="294.74" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2758;0.2762;1.0000" values="0;0;1;1"/></circle>
<circle cx="68.15" cy="139.17" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2853;0.2857;1.0000" values="0;0;1;1"/></circle>
<circle cx="326.52" cy="202.68" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2949;0.2952;1.0000" values="0;0;1;1"/></circle>
<circle cx="346.42" cy="184.97" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3044;0.3048;1.0000" values="0;0;1;1"/></circle>
<circle cx="88.74" cy="241.59" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3139;0.3143;1.0000" values="0;0;1;1"/></circle>
<circle cx="289.1" cy="153.83" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3234;0.3238;1.0000" values="0;0;1;1"/></circle>
<circle cx="92.75" cy="169.15" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3330;0.3333;1.0000" values="0;0;1;1"/></circle>
<circle cx="341.8" cy="272.96" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3425;0.3429;1.0000" values="0;0;1;1"/></circle>
<circle cx="101.51" cy="148.12" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3520;0.3524;1.0000" values="0;0;1;1"/></circle>
<circle cx="96.7" cy="102.61" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3615;0.3619;1.0000" values="0;0;1;1"/></circle>
<circle cx="294.35" cy="131.35" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3710;0.3714;1.0000" values="0;0;1;1"/></circle>
<circle cx="226.84" cy="197.17" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3806;0.3810;1.0000" values="0;0;1;1"/></circle>
<circle cx="122.15" cy="266.58" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3901;0.3905;1.0000" values="0;0;1;1"/></circle>
<circle cx="105.19" cy="245.07" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3996;0.4000;1.0000" values="0;0;1;1"/></circle>
<circle cx="101.09" cy="190.66" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4091;0.4095;1.0000" values="0;0;1;1"/></circle>
<circle cx="128.45" cy="153.83" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4187;0.4190;1.0000" values="0;0;1;1"/></circle>
<circle cx="343.74" cy="284.03" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4282;0.4286;1.0000" values="0;0;1;1"/></circle>
<circle cx="154.38" cy="303.91" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4377;0.4381;1.0000" values="0;0;1;1"/></circle>
<circle cx="127.84" cy="184.2" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4472;0.4476;1.0000" values="0;0;1;1"/></circle>
<circle cx="310.64" cy="244.61" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4568;0.4571;1.0000" values="0;0;1;1"/></circle>
<circle cx="96.49" cy="329.39" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4663;0.4667;1.0000" values="0;0;1;1"/></circle>
<circle cx="128.56" cy="151.02" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4758;0.4762;1.0000" values="0;0;1;1"/></circle>
<circle cx="287.44" cy="168.27" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4853;0.4857;1.0000" values="0;0;1;1"/></circle>
<circle cx="152.16" cy="105.91" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4949;0.4952;1.0000" values="0;0;1;1"/></circle>
<circle cx="93.59" cy="230.19" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5044;0.5048;1.0000" values="0;0;1;1"/></circle>
<circle cx="137.02" cy="234.71" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5139;0.5143;1.0000" values="0;0;1;1"/></circle>
<circle cx="173.56" cy="198.58" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5234;0.5238;1.0000" values="0;0;1;1"/></circle>
<circle cx="340.39" cy="206.03" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5330;0.5333;1.0000" values="0;0;1;1"/></circle>
<circle cx="231.18" cy="299.43" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5425;0.5429;1.0000" values="0;0;1;1"/></circle>
<circle cx="119.92" cy="125.61" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5520;0.5524;1.0000" values="0;0;1;1"/></circle>
<circle cx="325.99" cy="287.54" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5615;0.5619;1.0000" values="0;0;1;1"/></circle>
<circle cx="138.86" cy="134.31" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5710;0.5714;1.0000" values="0;0;1;1"/></circle>
<circle cx="278.0" cy="317.46" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5806;0.5810;1.0000" values="0;0;1;1"/></circle>
<circle cx="123.83" cy="319.83" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5901;0.5905;1.0000" values="0;0;1;1"/></circle>
<circle cx="318.54" cy="235.26" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5996;0.6000;1.0000" values="0;0;1;1"/></circle>
<circle cx="187.69" cy="113.34" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.6091;0.6095;1.0000" values="0;0;1;1"/></circle>
<circle cx="78.99" cy="322.89" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.6187;0.6190;1.0000" values="0;0;1;1"/></circle>
<circle cx="135.71" cy="259.92" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.6282;0.6286;1.0000" values="0;0;1;1"/></circle>
<circle cx="140.98" cy="288.99" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.6377;0.6381;1.0000" values="0;0;1;1"/></circle>
<circle cx="237.4" cy="159.6" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.6472;0.6476;1.0000" values="0;0;1;1"/></circle>
<rect x="420" y="80" width="300" height="260" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="570" y="70" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#64748b">ブルー ノイズ（近づきすぎない）</text>
<circle cx="477.82" cy="263.77" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0472;0.0476;1.0000" values="0;0;1;1"/></circle>
<circle cx="683.84" cy="300.55" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0568;0.0571;1.0000" values="0;0;1;1"/></circle>
<circle cx="564.59" cy="144.17" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0663;0.0667;1.0000" values="0;0;1;1"/></circle>
<circle cx="678.0" cy="181.8" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0758;0.0762;1.0000" values="0;0;1;1"/></circle>
<circle cx="449.21" cy="95.68" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0853;0.0857;1.0000" values="0;0;1;1"/></circle>
<circle cx="606.91" cy="247.83" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0949;0.0952;1.0000" values="0;0;1;1"/></circle>
<circle cx="685.37" cy="109.28" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1044;0.1048;1.0000" values="0;0;1;1"/></circle>
<circle cx="451.51" cy="195.58" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1139;0.1143;1.0000" values="0;0;1;1"/></circle>
<circle cx="516.52" cy="181.02" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1234;0.1238;1.0000" values="0;0;1;1"/></circle>
<circle cx="541.77" cy="283.46" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1330;0.1333;1.0000" values="0;0;1;1"/></circle>
<circle cx="623.12" cy="166.59" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1425;0.1429;1.0000" values="0;0;1;1"/></circle>
<circle cx="489.95" cy="331.6" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1520;0.1524;1.0000" values="0;0;1;1"/></circle>
<circle cx="621.8" cy="310.38" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1615;0.1619;1.0000" values="0;0;1;1"/></circle>
<circle cx="598.66" cy="91.23" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1710;0.1714;1.0000" values="0;0;1;1"/></circle>
<circle cx="483.42" cy="128.28" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1806;0.1810;1.0000" values="0;0;1;1"/></circle>
<circle cx="711.97" cy="244.71" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1901;0.1905;1.0000" values="0;0;1;1"/></circle>
<circle cx="440.81" cy="314.96" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1996;0.2000;1.0000" values="0;0;1;1"/></circle>
<circle cx="512.08" cy="91.42" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2091;0.2095;1.0000" values="0;0;1;1"/></circle>
<circle cx="704.38" cy="147.46" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2187;0.2190;1.0000" values="0;0;1;1"/></circle>
<circle cx="648.94" cy="217.51" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2282;0.2286;1.0000" values="0;0;1;1"/></circle>
<circle cx="533.98" cy="204.77" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2377;0.2381;1.0000" values="0;0;1;1"/></circle>
<circle cx="588.24" cy="206.31" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2472;0.2476;1.0000" values="0;0;1;1"/></circle>
<circle cx="451.21" cy="162.13" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2568;0.2571;1.0000" values="0;0;1;1"/></circle>
<circle cx="483.37" cy="225.57" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2663;0.2667;1.0000" values="0;0;1;1"/></circle>
<circle cx="583.3" cy="280.29" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2758;0.2762;1.0000" values="0;0;1;1"/></circle>
<circle cx="662.65" cy="250.68" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2853;0.2857;1.0000" values="0;0;1;1"/></circle>
<circle cx="648.37" cy="131.78" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2949;0.2952;1.0000" values="0;0;1;1"/></circle>
<circle cx="583.45" cy="321.51" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3044;0.3048;1.0000" values="0;0;1;1"/></circle>
<circle cx="519.39" cy="151.3" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3139;0.3143;1.0000" values="0;0;1;1"/></circle>
<circle cx="530.16" cy="255.65" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3234;0.3238;1.0000" values="0;0;1;1"/></circle>
<circle cx="431.51" cy="180.02" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3330;0.3333;1.0000" values="0;0;1;1"/></circle>
<circle cx="543.54" cy="105.73" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3425;0.3429;1.0000" values="0;0;1;1"/></circle>
<circle cx="645.79" cy="288.35" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3520;0.3524;1.0000" values="0;0;1;1"/></circle>
<circle cx="606.1" cy="136.29" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3615;0.3619;1.0000" values="0;0;1;1"/></circle>
<circle cx="509.96" cy="306.87" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3710;0.3714;1.0000" values="0;0;1;1"/></circle>
<circle cx="437.09" cy="131.94" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3806;0.3810;1.0000" values="0;0;1;1"/></circle>
<circle cx="561.45" cy="188.39" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3901;0.3905;1.0000" values="0;0;1;1"/></circle>
<circle cx="442.76" cy="257.56" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3996;0.4000;1.0000" values="0;0;1;1"/></circle>
<circle cx="455.99" cy="281.34" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4091;0.4095;1.0000" values="0;0;1;1"/></circle>
<circle cx="677.84" cy="330.88" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4187;0.4190;1.0000" values="0;0;1;1"/></circle>
<circle cx="491.4" cy="162.95" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4282;0.4286;1.0000" values="0;0;1;1"/></circle>
<circle cx="480.93" cy="306.88" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4377;0.4381;1.0000" values="0;0;1;1"/></circle>
<circle cx="537.26" cy="314.74" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4472;0.4476;1.0000" values="0;0;1;1"/></circle>
<circle cx="502.68" cy="282.84" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4568;0.4571;1.0000" values="0;0;1;1"/></circle>
<circle cx="703.63" cy="98.28" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4663;0.4667;1.0000" values="0;0;1;1"/></circle>
<circle cx="708.08" cy="123.28" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4758;0.4762;1.0000" values="0;0;1;1"/></circle>
<circle cx="488.9" cy="202.12" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4853;0.4857;1.0000" values="0;0;1;1"/></circle>
<circle cx="530.55" cy="125.46" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4949;0.4952;1.0000" values="0;0;1;1"/></circle>
<circle cx="582.49" cy="121.19" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5044;0.5048;1.0000" values="0;0;1;1"/></circle>
<circle cx="673.94" cy="143.15" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5139;0.5143;1.0000" values="0;0;1;1"/></circle>
<circle cx="496.11" cy="110.7" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5234;0.5238;1.0000" values="0;0;1;1"/></circle>
<circle cx="681.26" cy="226.03" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5330;0.5333;1.0000" values="0;0;1;1"/></circle>
<circle cx="428.26" cy="220.69" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5425;0.5429;1.0000" values="0;0;1;1"/></circle>
<circle cx="568.19" cy="246.64" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5520;0.5524;1.0000" values="0;0;1;1"/></circle>
<circle cx="654.19" cy="183.72" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5615;0.5619;1.0000" values="0;0;1;1"/></circle>
<circle cx="480.44" cy="91.35" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5710;0.5714;1.0000" values="0;0;1;1"/></circle>
<circle cx="623.27" cy="190.31" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5806;0.5810;1.0000" values="0;0;1;1"/></circle>
<circle cx="706.6" cy="183.0" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5901;0.5905;1.0000" values="0;0;1;1"/></circle>
<circle cx="681.51" cy="163.48" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5996;0.6000;1.0000" values="0;0;1;1"/></circle>
<circle cx="663.06" cy="275.32" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.6091;0.6095;1.0000" values="0;0;1;1"/></circle>
<circle cx="614.58" cy="285.82" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.6187;0.6190;1.0000" values="0;0;1;1"/></circle>
<circle cx="542.55" cy="166.45" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.6282;0.6286;1.0000" values="0;0;1;1"/></circle>
<circle cx="505.64" cy="253.24" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.6377;0.6381;1.0000" values="0;0;1;1"/></circle>
<circle cx="637.24" cy="329.42" r="5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.6472;0.6476;1.0000" values="0;0;1;1"/></circle>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">点を 64 個ずつ置いていく<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5710;0.5714;1.0000" values="1;1;0;0"/></text>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">左: 固まりと隙間ができる（ぼかしても低周波の斑が残る）／ 右: 均一なのでぼかしで消えやすい<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.5710;0.5714;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:noise-points:end -->

### ホワイト ノイズ

画素ごとに完全に独立な乱数を使う、最も単純なノイズです。偶然、似た値が近くに集まる（クラスタができる）ことがあり、そのクラスタは低周波の斑として、ぼかしても残ります。「ぼかしたのに、まだ汚れている」ときは、ホワイト ノイズが原因のことがよくあります。

### 4×4 のタイル テクスチャ

古典的な SSAO では、4×4 画素の小さなランダム回転テクスチャを画面全体に敷き詰めます。パターンの周期が 4 画素なので、<strong>4×4 のぼかしを掛ければ、タイル 1 枚分の 16 通りの回転がちょうど平均されて消えます</strong>。ぼかしの大きさとノイズの周期を合わせる、という設計です。簡単ですが、ぼかしを小さくするとタイルの繰り返しが見えます。

### Interleaved Gradient Noise（IGN）

Jimenez が 2014 年に紹介したノイズで、<strong>画素の座標だけから式で計算できる</strong>ので、テクスチャが要りません。

```hlsl
float InterleavedGradientNoise(float2 pixel) {
  return frac(52.9829189 * frac(dot(pixel, float2(0.06711056, 0.00583715))));
}
```

隣り合う画素で値が滑らかに変化するように作られており、近い画素どうしがなるべく「離れた値」を取るので、低周波が少なく、ぼかしで消えやすい性質があります。画面全体で 1 つの式なので、フレーム番号を足して `pixel + frame * offset` のようにずらすだけで、時間方向にも異なるパターンになります。

### ブルー ノイズ

<strong>低周波がほとんど無い</strong>ことを狙って作られたノイズです。「近くに似た値が集まらない」よう最適化されているので、ぼかしできれいに消え、時間蓄積とも相性が良いです。欠点は、テクスチャとして事前に生成して持つ必要があること、および、サンプルの向きの選び方を工夫しないと、画面空間のパターンとして見えることです。品質を重視する実装（HBAO+ や GTAO の実装）は、ブルー ノイズや、それに近い低ディスクレパンシーな並びを使います。

### Bayer 配列（ディザ行列）

規則的な行列を敷き詰める方法です。規則的なので縞が出やすく、AO のサンプル回転には不向きです。ディザ透明のように、「規則性が見えても構わない」用途で使います（[Dithered Transparency](../../translucency/alpha-test/dither.md)）。

## 時間方向にもずらす

時間蓄積と組み合わせる場合は、パターンを<strong>フレームごとに変えます</strong>。同じパターンのまま履歴と混ぜても、同じ誤差が重なるだけで、サンプルが増えないからです。

よく使われるのは<strong>黄金比の数列</strong>です。フレーム番号 i に対して `frac(i × 0.61803398875)` を回転角のオフセットに足すと、この値は 0〜1 を<strong>偏りなく埋めるように</strong>並びます（どの区間にも、ほぼ同じ頻度で入る）。単純に「フレーム番号 mod N」で N 通りを順番に回す方法もありますが、N が小さいと周期が目に見えてしまうことがあります。

さらに、空間（画素）と時間（フレーム）の両方でずらせば、「ある画素で何フレーム経っても同じ向き」や「ある瞬間に画面全体で同じ向き」を避けられます。

## ノイズを、作るコード

AO のサンプルの向きは、画素ごとに、ずらします。ずらす値（ノイズ）は、シェーダーの中で、計算で作れます。

### Interleaved Gradient Noise（IGN）

画素の座標だけから、ブルー ノイズに近い値を、1 行で作ります（Jimenez）。テクスチャを読まないので、安く、TAA と相性が良いです。

```hlsl
// 画素の座標（SV_Position.xy）から、0〜1 のノイズを作る。
float InterleavedGradientNoise(float2 pixel) {
  return frac(52.9829189 * frac(dot(pixel, float2(0.06711056, 0.00583715))));
}

// フレームごとに、ずらして、時間方向にも、ばらつかせる（TAA や時間蓄積が、平均してくれる）。
float IgnTemporal(float2 pixel, uint frame) {
  return InterleavedGradientNoise(pixel + 5.588238 * (frame % 64));
}
```

### ブルー ノイズ テクスチャ

あらかじめ作った、ブルー ノイズの、小さな画像（64×64 など）を、画面に敷き詰めて、読みます。

```hlsl
Texture2D<float> g_blue_noise : register(t6);      // 64×64、R8_UNORM。WRAP サンプラーで、繰り返す

float BlueNoise(uint2 pixel, uint frame) {
  float n = g_blue_noise.Load(int3(pixel % 64, 0));
  // 黄金比で、フレームごとにずらす（0〜1 を、均等に巡る）。
  return frac(n + 0.61803398875 * (frame % 64));
}
```

| 方式 | 見た目 | コスト |
| --- | --- | --- |
| `frac(sin(…))` のハッシュ | 白色ノイズ。粒が目立つ | 最小（ただし、GPU ごとに、結果が違う） |
| IGN | ブルー ノイズに近い。縞は出にくい | 最小（計算だけ） |
| ブルー ノイズ テクスチャ | 最も、粒が細かく、均一 | 読み込み 1 回 |
| 4×4 のタイル テクスチャ | 4 画素周期の模様が出る。4×4 のぼかしで消せる | 読み込み 1 回 |

### ノイズを、サンプルの向きに使う

```hlsl
float noise = IgnTemporal(pos.xy, g_frame_index);               // 0〜1
float rotation = noise * 6.2831853;                             // 画素ごとに、サンプル全体を、回す角度
float2x2 rot = float2x2(cos(rotation), -sin(rotation), sin(rotation), cos(rotation));
for (int i = 0; i < kSamples; ++i) {
  float2 offset = mul(kernel[i].xy, rot);                       // 回したサンプル位置で、深度を読む
  ...
}
```

回転の角度が、画素ごとに違うので、同じ向きの取りこぼし（縞）が、細かい粒に変わり、ぼかしと、時間蓄積で、均されます。フレームごとに、ずらすのは、<strong>1 フレームだけでは、足りない分を、時間で、補う</strong>ためです（[Temporal Accumulation](temporal.md)）。

## よくあるミス

??? failure "ノイズを全画素で同じにして、規則的な縞が見える"
    <strong>画素ごとに違う回転</strong>（ノイズ）にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 画素ごとに回転して、縞をノイズに変える
    - [x] ブルー ノイズが、フィルタで消えやすい

## 参考

- Georgiev, Fajardo, "Blue-Noise Dithered Sampling", SIGGRAPH 2016 Talks
- Heitz, Belcour, Ostromoukhov, Coeurjolly, Iehl, "A Low-Discrepancy Sampler that Distributes Monte Carlo Errors as a Blue Noise in Screen Space", SIGGRAPH 2019 Talks
- Bavoil, Jansen, "Particle Shadows & Cache-Efficient Post-Processing", GDC 2013（デインターリーブ テクスチャリング）
- de Vries, "SSAO", LearnOpenGL（半球カーネル・ノイズ・バイアス・範囲チェックの、実装解説）

## 関連ページ

- [AO Filtering](index.md)
- [Temporal Accumulation](temporal.md)
- [Bilateral Blur](bilateral-blur.md)
