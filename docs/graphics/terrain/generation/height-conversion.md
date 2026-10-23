---
title: Converting Noise to Height
tags:
  - 描画
---

# Converting Noise to Height

<strong>ノイズの値をそのまま高さにすると、平らな所と山が同じ比率になって不自然</strong>です。カーブを通して平地を広く山を高くすると、地形らしくなります。このページではノイズから高さへの変換を説明します。

!!! tip "ポイント"
    - カーブで分布を整える（平地を広く）。
    - 海面より下は平らに。
    - 高さに応じてノイズの種類を変える。
    - スケール（高さの最大）を調整。

## 地形の高さへの変換
<strong>ノイズ値をそのまま高さにするのではなく、形を整えます</strong>。

| 工夫 | 内容 |
| --- | --- |
| べき乗 | `pow(h, 2.0)` で平地を広く、山を急に |
| 大陸の形 | 低周波のノイズで陸と海の分布を作り、山のノイズを陸にだけ掛ける |
| 高さの段差（テラス） | `floor` で段にし、少し滑らかに |
| 島の形 | 中心から離れるほど、高さを下げる（円のマスク） |
| バイオーム | 高さ・湿度（別のノイズ）で、地面の種類を決める |

<!-- fig:height-pow-curve:begin -->

<svg class="fig illust motion" data-fig="height-pow-curve" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-height-pow-curve" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">ノイズを高さに直す: 冪(べき)を掛けると、平野が広がり、山が尖る</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 次元のノイズ(−1〜1)を、高さ ((n+1)/2)^p にする。p = 1・2・3 で、海面より下(0.3 以下)の割合と、山の鋭さを計算する</text>
<rect x="60.0" y="110" width="840.0" height="84" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="60.0" y="168.8" width="840.0" height="25.2" fill="#bae6fd" opacity="0.6"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/><path d="M60.0,193.84 L65.28,188.95 L70.57,180.45 L75.85,171.54 L81.13,166.61 L86.42,166.09 L91.7,166.29 L96.98,167.76 L102.26,167.92 L107.55,172.73 L112.83,185.17 L118.11,193.79 L123.4,194.0 L128.68,194.0 L133.96,194.0 L139.25,194.0 L144.53,193.35 L149.81,191.98 L155.09,185.91 L160.38,173.68 L165.66,165.44 L170.94,158.75 L176.23,147.53 L181.51,140.19 L186.79,141.24 L192.08,138.02 L197.36,134.79 L202.64,131.84 L207.92,129.62 L213.21,128.72 L218.49,128.45 L223.77,131.08 L229.06,134.68 L234.34,143.66 L239.62,152.63 L244.91,159.66 L250.19,170.6 L255.47,178.25 L260.75,184.79 L266.04,189.63 L271.32,187.57 L276.6,184.98 L281.89,183.21 L287.17,187.9 L292.45,193.97 L297.74,194.0 L303.02,194.0 L308.3,194.0 L313.58,194.0 L318.87,190.06 L324.15,189.42 L329.43,185.12 L334.72,177.25 L340.0,168.47 L345.28,156.49 L350.57,147.13 L355.85,142.59 L361.13,145.15 L366.42,148.52 L371.7,151.15 L376.98,150.72 L382.26,147.62 L387.55,151.03 L392.83,155.54 L398.11,155.38 L403.4,152.48 L408.68,146.84 L413.96,145.23 L419.25,144.45 L424.53,145.6 L429.81,147.79 L435.09,145.59 L440.38,146.97 L445.66,155.31 L450.94,162.74 L456.23,166.68 L461.51,177.34 L466.79,185.8 L472.08,186.03 L477.36,184.23 L482.64,179.05 L487.92,174.13 L493.21,168.94 L498.49,166.55 L503.77,166.64 L509.06,168.42 L514.34,170.14 L519.62,164.91 L524.91,158.47 L530.19,153.1 L535.47,144.03 L540.75,137.41 L546.04,128.84 L551.32,121.48 L556.6,118.29 L561.89,121.7 L567.17,131.44 L572.45,136.54 L577.74,136.49 L583.02,140.38 L588.3,145.55 L593.58,144.97 L598.87,149.53 L604.15,159.89 L609.43,166.19 L614.72,173.05 L620.0,175.16 L625.28,173.04 L630.57,169.67 L635.85,169.17 L641.13,171.74 L646.42,173.45 L651.7,174.61 L656.98,173.44 L662.26,176.96 L667.55,188.2 L672.83,194.0 L678.11,194.0 L683.4,194.0 L688.68,194.0 L693.96,194.0 L699.25,194.0 L704.53,194.0 L709.81,194.0 L715.09,194.0 L720.38,194.0 L725.66,194.0 L730.94,191.66 L736.23,189.26 L741.51,193.17 L746.79,190.66 L752.08,185.97 L757.36,179.35 L762.64,171.2 L767.92,162.06 L773.21,151.69 L778.49,142.97 L783.77,134.64 L789.06,131.75 L794.34,129.57 L799.62,126.83 L804.91,128.93 L810.19,128.06 L815.47,126.76 L820.75,124.82 L826.04,117.4 L831.32,114.0 L836.6,114.0 L841.89,114.0 L847.17,120.28 L852.45,122.17 L857.74,125.22 L863.02,131.98 L868.3,133.05 L873.58,130.17 L878.87,133.57 L884.15,134.26 L889.43,132.01 L894.72,129.16 L900.0,123.11" fill="none" stroke="#2563eb" stroke-width="3"/>
<text x="68.0" y="126" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb">p = 1</text>
<text x="892.0" y="126" text-anchor="end" style="font-size:13px;font-weight:700;fill:#1f2937">海面より下 41% / 高い山(0.7 以上)24%</text>
</g>
<rect x="60.0" y="208" width="840.0" height="84" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="60.0" y="266.8" width="840.0" height="25.2" fill="#bae6fd" opacity="0.6"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3109;0.3111;1.0000" values="0;0;1;1"/><path d="M60.0,292.0 L65.28,291.68 L70.57,289.7 L75.85,285.69 L81.13,282.63 L86.42,282.26 L91.7,282.4 L96.98,283.4 L102.26,283.5 L107.55,286.34 L112.83,291.03 L118.11,292.0 L123.4,292.0 L128.68,292.0 L133.96,292.0 L139.25,292.0 L144.53,291.99 L149.81,291.95 L155.09,291.18 L160.38,286.84 L165.66,281.8 L170.94,276.47 L176.23,265.01 L181.51,255.8 L186.79,257.21 L192.08,252.83 L197.36,248.18 L202.64,243.71 L207.92,240.19 L213.21,238.73 L218.49,238.29 L223.77,242.52 L229.06,248.02 L234.34,260.32 L239.62,270.61 L244.91,277.26 L250.19,285.15 L255.47,288.9 L260.75,290.94 L266.04,291.76 L271.32,291.48 L276.6,290.98 L281.89,290.55 L287.17,291.53 L292.45,292.0 L297.74,292.0 L303.02,292.0 L308.3,292.0 L313.58,292.0 L318.87,291.81 L324.15,291.74 L329.43,291.01 L334.72,288.49 L340.0,283.85 L345.28,274.41 L350.57,264.54 L355.85,258.97 L361.13,262.18 L366.42,266.14 L371.7,269.05 L376.98,268.58 L382.26,265.11 L387.55,268.92 L392.83,273.51 L398.11,273.35 L403.4,270.45 L408.68,264.2 L413.96,262.27 L419.25,261.32 L424.53,262.72 L429.81,265.31 L435.09,262.7 L440.38,264.35 L445.66,273.29 L450.94,279.78 L456.23,282.67 L461.51,288.53 L466.79,291.16 L472.08,291.21 L477.36,290.81 L482.64,289.21 L487.92,287.07 L493.21,284.15 L498.49,282.58 L503.77,282.64 L509.06,283.82 L514.34,284.88 L519.62,281.42 L524.91,276.22 L530.19,271.09 L535.47,260.79 L540.75,251.98 L546.04,238.92 L551.32,226.26 L556.6,220.35 L561.89,226.66 L567.17,243.07 L572.45,250.73 L577.74,250.65 L583.02,256.06 L588.3,262.66 L593.58,261.96 L598.87,267.28 L604.15,277.45 L609.43,282.33 L614.72,286.51 L620.0,287.56 L625.28,286.51 L630.57,284.6 L635.85,284.3 L641.13,285.8 L646.42,286.72 L651.7,287.3 L656.98,286.72 L662.26,288.37 L667.55,291.58 L672.83,292.0 L678.11,292.0 L683.4,292.0 L688.68,292.0 L693.96,292.0 L699.25,292.0 L704.53,292.0 L709.81,292.0 L715.09,292.0 L720.38,292.0 L725.66,292.0 L730.94,291.93 L736.23,291.72 L741.51,291.99 L746.79,291.86 L752.08,291.19 L757.36,289.32 L762.64,285.5 L767.92,279.25 L773.21,269.62 L778.49,259.45 L783.77,247.95 L789.06,243.56 L794.34,240.12 L799.62,235.61 L804.91,239.07 L810.19,237.65 L815.47,235.49 L820.75,232.18 L826.04,218.66 L831.32,212.0 L836.6,212.0 L841.89,212.0 L847.17,224.06 L852.45,227.5 L857.74,232.87 L863.02,243.91 L868.3,245.56 L873.58,241.06 L878.87,246.35 L884.15,247.38 L889.43,243.97 L894.72,239.45 L900.0,229.18" fill="none" stroke="#2ea043" stroke-width="3"/>
<text x="68.0" y="224" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2ea043">p = 2</text>
<text x="892.0" y="224" text-anchor="end" style="font-size:13px;font-weight:700;fill:#1f2937">海面より下 62% / 高い山(0.7 以上)9%</text>
</g>
<rect x="60.0" y="306" width="840.0" height="84" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="60.0" y="364.8" width="840.0" height="25.2" fill="#bae6fd" opacity="0.6"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5554;0.5556;1.0000" values="0;0;1;1"/><path d="M60.0,390.0 L65.28,389.98 L70.57,389.61 L75.85,388.23 L81.13,386.79 L86.42,386.6 L91.7,386.68 L96.98,387.18 L102.26,387.23 L107.55,388.5 L112.83,389.89 L118.11,390.0 L123.4,390.0 L128.68,390.0 L133.96,390.0 L139.25,390.0 L144.53,390.0 L149.81,390.0 L155.09,389.92 L160.38,388.69 L165.66,386.36 L170.94,383.16 L176.23,374.32 L181.51,365.65 L186.79,367.06 L192.08,362.59 L197.36,357.56 L202.64,352.48 L207.92,348.31 L213.21,346.53 L218.49,346.0 L223.77,351.09 L229.06,357.39 L234.34,370.06 L239.62,378.94 L244.91,383.67 L250.19,388.0 L255.47,389.39 L260.75,389.88 L266.04,389.99 L271.32,389.96 L276.6,389.89 L281.89,389.8 L287.17,389.96 L292.45,390.0 L297.74,390.0 L303.02,390.0 L308.3,390.0 L313.58,390.0 L318.87,389.99 L324.15,389.99 L329.43,389.89 L334.72,389.27 L340.0,387.4 L345.28,381.75 L350.57,373.91 L355.85,368.77 L361.13,371.79 L366.42,375.3 L371.7,377.71 L376.98,377.33 L382.26,374.41 L387.55,377.6 L392.83,381.11 L398.11,381.0 L403.4,378.82 L408.68,373.61 L413.96,371.88 L419.25,371.0 L424.53,372.28 L429.81,374.59 L435.09,372.27 L440.38,373.74 L445.66,380.95 L450.94,385.22 L456.23,386.82 L461.51,389.28 L466.79,389.91 L472.08,389.92 L477.36,389.85 L482.64,389.48 L487.92,388.77 L493.21,387.54 L498.49,386.77 L503.77,386.8 L509.06,387.39 L514.34,387.88 L519.62,386.15 L524.91,382.99 L530.19,379.31 L535.47,370.51 L540.75,361.69 L546.04,346.77 L551.32,330.41 L556.6,322.19 L561.89,330.95 L567.17,351.73 L572.45,360.36 L577.74,360.27 L583.02,365.91 L588.3,372.23 L593.58,371.59 L598.87,376.26 L604.15,383.8 L609.43,386.64 L614.72,388.56 L620.0,388.96 L625.28,388.56 L630.57,387.75 L635.85,387.61 L641.13,388.28 L646.42,388.64 L651.7,388.86 L656.98,388.64 L662.26,389.23 L667.55,389.97 L672.83,390.0 L678.11,390.0 L683.4,390.0 L688.68,390.0 L693.96,390.0 L699.25,390.0 L704.53,390.0 L709.81,390.0 L715.09,390.0 L720.38,390.0 L725.66,390.0 L730.94,390.0 L736.23,389.98 L741.51,390.0 L746.79,389.99 L752.08,389.92 L757.36,389.51 L762.64,388.15 L767.92,384.91 L773.21,378.16 L778.49,369.24 L783.77,357.31 L789.06,352.3 L794.34,348.22 L799.62,342.65 L804.91,346.94 L810.19,345.2 L815.47,342.5 L820.75,338.27 L826.04,319.78 L831.32,310.0 L836.6,310.0 L841.89,310.0 L847.17,327.39 L852.45,332.08 L857.74,339.17 L863.02,352.72 L868.3,354.62 L873.58,349.36 L878.87,355.51 L884.15,356.68 L889.43,352.78 L894.72,347.41 L900.0,334.33" fill="none" stroke="#e5484d" stroke-width="3"/>
<text x="68.0" y="322" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d">p = 3</text>
<text x="892.0" y="322" text-anchor="end" style="font-size:13px;font-weight:700;fill:#1f2937">海面より下 74% / 高い山(0.7 以上)6%</text>
</g>
<text x="40" y="410" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">海面より下の割合(%):</text>
<text x="240" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#2563eb" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0887;0.0889;1.0000" values="1;1;0;0"/></text>
<text x="240" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#2563eb" opacity="0">41<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0887;0.0889;0.3332;0.3333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#2563eb" opacity="0">62<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3332;0.3333;0.5776;0.5778;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#2563eb" opacity="0">74<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5776;0.5778;1.0000" values="0;0;1;1"/></text>
<text x="40" y="448" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">高い山の割合(%):</text>
<text x="240" y="452" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0887;0.0889;1.0000" values="1;1;0;0"/></text>
<text x="240" y="452" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">24<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0887;0.0889;0.3332;0.3333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="452" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">9<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3332;0.3333;0.5776;0.5778;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="452" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">6<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5776;0.5778;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7865;0.7867;1.0000" values="0;0;1;1"/><rect x="420" y="400" width="510" height="90" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="436" y="424" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">p を上げると、低い所が広がり(41% → 74%)、</text>
<text x="436" y="447" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">高い山は、少数の尖った所だけが残る(24% → 6%)</text>
<text x="436" y="470" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">同じノイズから、島・平野・山脈と、地形の雰囲気を作り分けられる</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ノイズの値を、そのまま高さにすると、丸い起伏になる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">冪を掛けると、平野が広がり、山が目立つ<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.7998;0.8000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">p が地形の個性を決める<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7998;0.8000;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:height-pow-curve:end -->

## ノイズの値はそのままでは、地形の高さにならない

[fBm](fbm.md) や[リッジ ノイズ](ridge.md) の出力は、<strong>−1〜1（または 0〜1）の数字</strong>です。これを メートル単位の高さにする作業が、「高さへの変換」です。単にスケールを掛けるだけでも地形になりますが、ひと工夫するだけで見た目が大きく変わります。

## 1. 線形のスケール

```text
height = noise × max_height + base_height
```

最も単純です。高さが均等に分布するので <strong>山頂も谷も、同じくらいの数</strong>になります。自然の地形は 平地（低い所）が広く山は、少ししかないので人工的に見えます。

## 2. べき乗で平地を広げる

ノイズの値（0〜1）を <strong>べき乗</strong>すると、低い値がさらに低くなります。

```hlsl
float h = pow(saturate(noise01), 2.0);      // 2 乗: 低い所が、ぺたんと平らに
```

| 指数 | 見た目 |
| --- | --- |
| 1.0 | 線形。起伏が均等 |
| 2.0 | 平地が広がり山が、鋭く残る |
| 3.0 以上 | ほとんどが平地。山はごく一部 |
| 0.5 以下 | 山の頂上が、平らになる（台地、メサ） |

## 3. 高さの分布をカーブで変える

べき乗より細かく制御したいときは、<strong>入力（ノイズ）と出力（高さ）の対応を、カーブで描いて</strong>、テーブルとして引きます。

```text
出力
  1.0 |                ●────●
      |             ●
  0.5 |        ●───●        ← 平らな高原
      |    ●
  0.0 |●──●                 ← 平らな海底・平野
      +──────────────────── 入力
      0                  1
```

```cpp
// 制御点（入力, 出力）を並べて、区間ごとに、線形補間する。
struct CurvePoint { float in; float out; };

float EvaluateCurve(const std::vector<CurvePoint>& curve, float x) {
  if (x <= curve.front().in) return curve.front().out;
  for (size_t i = 1; i < curve.size(); ++i) {
    if (x <= curve[i].in) {
      const float t = (x - curve[i - 1].in) / (curve[i].in - curve[i - 1].in);
      return curve[i - 1].out + t * (curve[i].out - curve[i - 1].out);
    }
  }
  return curve.back().out;
}
```

アーティストが グラフを手で描いて、地形の性格を調整できます。GPU ではカーブを 1 次元のテクスチャ（256 画素）に焼いて、`SampleLevel` で引きます。

```hlsl
Texture1D<float> g_height_curve : register(t3);
float h = g_height_curve.SampleLevel(g_linear_clamp, saturate(noise01), 0);
```

## 4. 階段状にする（テラス）

高さを <strong>階段状</strong>に切ると 棚田や、段々の高原ができます。

```hlsl
// 高さを、steps 段の階段にする。sharpness が大きいほど、段が、はっきりする。
float Terrace(float h, float steps, float sharpness) {
  float x = h * steps;
  float f = frac(x);
  // 段の中は、ほぼ平らに、段の境目で、急に上がる
  float s = smoothstep(0.5 - 0.5 / sharpness, 0.5 + 0.5 / sharpness, f);
  return (floor(x) + s) / steps;
}
```

## 5. 複数のノイズを領域ごとに混ぜる

大陸規模の地形は 1 つのノイズでは、表現できません。<strong>複数の性格の違うノイズをマスクで混ぜます</strong>。

| 層 | ノイズ | 内容 |
| --- | --- | --- |
| 大陸性（continentalness） | 低周波の fBm | 陸か海か（高さの下地） |
| 地形の起伏（roughness） | 中周波の fBm | その場所が平らか、起伏が大きいか |
| 山脈 | リッジ ノイズ | 山のある場所だけ、足す |
| 細部 | 高周波の fBm | 小さな凹凸 |

```hlsl
float continent = Fbm(p * 0.001, 4, 2.0, 0.5, seed) * 0.5 + 0.5;    // 0 = 海、1 = 陸
float base = EvaluateBaseHeight(continent);                          // カーブで、海底〜陸の高さへ
float mountain_mask = smoothstep(0.55, 0.75, continent);             // 内陸だけ、山
float mountains = RidgedMulti(p * 0.003, 6, 2.0, 0.5, 1.0, 2.0, seed + 1) * mountain_mask;
float detail = Fbm(p * 0.02, 4, 2.0, 0.5, seed + 2) * 0.05;
float height = base + mountains * 800.0 + detail * 50.0;             // メートル
```

これで「海岸線の近くは平地。内陸に行くと山脈」という 地形の流れが作れます。

## 6. 高さマップの形式と単位

| 項目 | 内容 |
| --- | --- |
| 保存形式 | `R16_UNORM`（0〜65535）。高さの範囲を `height_scale`（メートル）で、決める |
| 解像度（高さ方向） | 16 ビットなら、最大高さ 1,000 m で、約 1.5 cm の刻み。8 ビットは 4 m の刻みで階段が、見える |
| 海面 | 海面を高さ 0 にするか、ある高さにするか先に決める。後から変えにくい |
| 範囲 | 保存の前に `saturate` で、0〜1 に収める。範囲を超えた値は切れる |

```cpp
// 高さ（メートル）→ R16_UNORM に変換
uint16_t EncodeHeight(float meters, float min_height, float max_height) {
  const float t = (meters - min_height) / (max_height - min_height);
  return static_cast<uint16_t>(std::clamp(t, 0.0f, 1.0f) * 65535.0f + 0.5f);
}
```

## 注意点

| 項目 | 内容 |
| --- | --- |
| 変換の順番 | べき乗やカーブの後に、侵食をかける（侵食は傾きに依存する）。逆にすると、侵食が変換で崩れる |
| 傾き | 高さのスケールを、2 倍にすると傾きも 2 倍になる。傾きの条件（岩、雪）はスケールの後の値で考える |
| ワールドの大きさ | 水平方向のスケール（1 テクセル何メートルか）と、垂直方向のスケールを合わせて決める。縦だけ伸ばすと針の山になる |

## よくあるミス

??? failure "どこも似た起伏で、変化が無い"
    <strong>カーブで平地と山の差を付ける</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] カーブで、高さの分布を整える

## 参考

- Ebert, Musgrave, Peachey, Perlin, Worley, "Texturing and Modeling: A Procedural Approach", 3rd Edition, Morgan Kaufmann, 2002（fBm、マルチフラクタル、リッジ ノイズ）
- Galin, Guérin, Peytavie, Cordonnier, Cani, Beneš, Gain, "A Review of Digital Terrain Modeling", Computer Graphics Forum (Eurographics 2019 STAR)
- Musgrave, Kolb, Mace, "The Synthesis and Rendering of Eroded Fractal Terrains", SIGGRAPH 1989

## 関連ページ

- [Terrain Generation](index.md)
- [fBm](fbm.md)
