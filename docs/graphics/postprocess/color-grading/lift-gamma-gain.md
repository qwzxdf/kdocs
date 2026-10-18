---
title: Lift, Gamma, Gain
tags:
  - 描画
---

# Lift, Gamma, Gain

<strong>リフト・ガンマ・ゲイン（LGG）</strong>は、<strong>映画のカラー グレーディングで定番の 3 つのつまみ</strong>で、<strong>暗部（リフト）・中間（ガンマ）・明部（ゲイン）を、別々に調整</strong>します。<strong>「暗い所は青く、明るい所は暖かく」</strong>のように明るさの領域ごとに色味を変える表現が簡単にできます。このページでは、3 つの役割・式・ASC CDL（スロープ・オフセット・パワー）との関係・色（RGB）ごとの調整・シャドウ/ミッド/ハイライトのカラー バランスを説明します。

!!! tip "ポイント"
    - <strong>ゲイン</strong> ＝ <strong>掛け算</strong>。<strong>明部</strong>に<strong>強く効く</strong>（<strong>傾き</strong>）。
    - <strong>リフト</strong> ＝ <strong>足し算</strong>。<strong>暗部</strong>に<strong>強く効く</strong>（<strong>黒の持ち上げ</strong>）。
    - <strong>ガンマ</strong> ＝ <strong>べき乗</strong>。<strong>中間調</strong>の<strong>明るさ</strong>を変える。
    - <strong>RGB 別々に</strong>調整できる → <strong>領域ごとの色味づけ</strong>（<strong>ティール＆オレンジ</strong>など）。
    - <strong>ASC CDL</strong> は<strong>業界標準の形式</strong>（<strong>スロープ・オフセット・パワー・彩度</strong>）。
    - <strong>ゲーム</strong>では<strong>リニアでなく、ガンマ・対数空間</strong>で<strong>行う</strong>と<strong>感覚が合う</strong>。

## 3 つのつまみ

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="リフト・ガンマ・ゲイン">
<text x="20" y="26" class="fig-title">3 つのつまみは、トーン曲線の別々の部分を動かす</text>
<g transform="translate(30,50)">
<text x="0" y="-6" style="font-size:13px;font-weight:700">リフト（暗部）</text>
<line x1="0" y1="150" x2="200" y2="150" stroke="currentColor" stroke-opacity="0.4"/><line x1="0" y1="0" x2="0" y2="150" stroke="currentColor" stroke-opacity="0.4"/>
<polyline fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4 3" points="0,150 200,0"/>
<polyline fill="none" stroke="#2563eb" stroke-width="3" points="0,110 200,0"/>
<text x="0" y="172" style="font-size:12px">黒が持ち上がる</text>
</g>
<g transform="translate(280,50)">
<text x="0" y="-6" style="font-size:13px;font-weight:700">ガンマ（中間）</text>
<line x1="0" y1="150" x2="200" y2="150" stroke="currentColor" stroke-opacity="0.4"/><line x1="0" y1="0" x2="0" y2="150" stroke="currentColor" stroke-opacity="0.4"/>
<polyline fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4 3" points="0,150 200,0"/>
<polyline fill="none" stroke="#2ea043" stroke-width="3" points="0,150 30,110 70,76 120,44 200,0"/>
<text x="0" y="172" style="font-size:12px">中間が明るくなる</text>
</g>
<g transform="translate(530,50)">
<text x="0" y="-6" style="font-size:13px;font-weight:700">ゲイン（明部）</text>
<line x1="0" y1="150" x2="200" y2="150" stroke="currentColor" stroke-opacity="0.4"/><line x1="0" y1="0" x2="0" y2="150" stroke="currentColor" stroke-opacity="0.4"/>
<polyline fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4 3" points="0,150 200,0"/>
<polyline fill="none" stroke="#e5484d" stroke-width="3" points="0,150 150,0"/>
<text x="0" y="172" style="font-size:12px">傾きが変わる（明部が強く動く）</text>
</g>
</svg>

| つまみ | 操作 | 影響が大きい範囲 |
| --- | --- | --- |
| <strong>ゲイン（Gain）</strong> | 掛ける | 明部（黒（0）は動かない） |
| <strong>リフト（Lift）</strong> | 足す | 暗部（白（1）は、ほぼ動かない） |
| <strong>ガンマ（Gamma）</strong> | べき乗 | 中間調（0 と 1 は動かない） |

## 式

```hlsl
float3 LiftGammaGain(float3 color, float3 lift, float3 gamma, float3 gain) {
  color = color * gain + lift;
  color = max(color, 0.0);
  return pow(color, 1.0 / gamma);
}
```

コードの要点です。`color * gain + lift` は、直線の傾き（ゲイン）と切片（リフト）を表します。`pow(color, 1 / gamma)` は中間調を曲げ、`gamma > 1` で明るくなります。各パラメータは `float3` で、RGB ごとに別の値を持つので、領域ごとの色味づけができます。

### リフトの別の定義

<strong>多くのツールでは、「リフトが白点を動かさない」よう</strong>に<strong>次の形</strong>にします。

<div class="formula">c' = gain · ( c + lift · (1 − c) )</div>

<strong>黒（c = 0）は `lift` だけ持ち上がり、白（c = 1）は変わりません</strong>。<strong>黒を沈めたり持ち上げたりする</strong>のが自然になります。

## ASC CDL（スロープ・オフセット・パワー）

<strong>ASC CDL</strong>（American Society of Cinematographers Color Decision List）は、<strong>映像業界で標準の色調整の交換形式</strong>です。LGG に近い 3 つのつまみ＋彩度で構成されます。

| ASC CDL | 対応 | 式 |
| --- | --- | --- |
| <strong>スロープ（Slope）</strong> | ゲイン | 掛ける |
| <strong>オフセット（Offset）</strong> | <strong>リフト（に近い）</strong> | 足す |
| <strong>パワー（Power）</strong> | <strong>ガンマ（の逆数）</strong> | べき乗 |
| <strong>彩度（Saturation）</strong> | 彩度 | 輝度との補間 |


CDL は、撮影現場とポストプロダクションの間で、色調整を数値で受け渡すための標準で、数値が少なく（3×3 + 彩度 1 の 10 個）、ツールを問わず同じ結果になるのが利点です。

CDL は、撮影現場とポストプロダクションの間で、色調整を数値で受け渡すための標準で、数値が少なく（3×3 + 彩度 1 の 10 個）、ツールを問わず同じ結果になるのが利点です。

<div class="formula">out = ( in × slope + offset ) ^ power　（その後、彩度）</div>

```hlsl
float3 ApplyCDL(float3 color, float3 slope, float3 offset, float3 power, float saturation) {
  float3 c = pow(max(color * slope + offset, 0.0), power);
  float luma = dot(c, float3(0.2126, 0.7152, 0.0722));
  return lerp(float3(luma, luma, luma), c, saturation);
}
```

<strong>Resolve・Nuke などのツールと、数値をやり取りできる</strong>ので、<strong>外部で作ったルックをゲームに持ち込めます</strong>。

## 領域ごとのカラー バランス

<strong>「暗部は青、中間はそのまま、明部は橙」</strong>のように<strong>明るさの領域に別々の色味を乗せる</strong>調整です。<strong>ティール＆オレンジ</strong>など、映画的なルックの定番です。

```hlsl
float3 ColorBalance(float3 color, float3 shadows, float3 midtones, float3 highlights) {
  float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
  float shadow_weight = 1.0 - smoothstep(0.0, 0.5, luma);
  float highlight_weight = smoothstep(0.5, 1.0, luma);
  float midtone_weight = 1.0 - shadow_weight - highlight_weight;
  return color + shadows * shadow_weight + midtones * midtone_weight + highlights * highlight_weight;
}
```

カラー バランスのコードの要点です。輝度で重みを決めて、暗部・中間・明部の重みを滑らかにします。`shadows` などは色のオフセット（RGB）で、小さい値（±0.05）を使います。用途として、ティール（暗部）とオレンジ（明部）にすると、肌が引き立ちます。

<!-- fig:color-lgg-curves:begin -->

<svg class="fig illust motion" data-fig="color-lgg-curves" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-color-lgg-curves" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">リフト・ガンマ・ゲイン: 暗い所(リフト)・中間(ガンマ)・明るい所(ゲイン)を、別々に動かす</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">入力 0〜1 → 出力。3 つのつまみを、1 つずつ動かして、暗部・中間・明部が、どれだけ動くかを計算する</text>
<rect x="30" y="96" width="480" height="340" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">曲線(青 = リフト、緑 = ガンマ、赤 = ゲイン)</text>
<path d="M70.0,410.0 L77.0,405.5 L84.0,401.0 L91.0,396.5 L98.0,392.0 L105.0,387.5 L112.0,383.0 L119.0,378.5 L126.0,374.0 L133.0,369.5 L140.0,365.0 L147.0,360.5 L154.0,356.0 L161.0,351.5 L168.0,347.0 L175.0,342.5 L182.0,338.0 L189.0,333.5 L196.0,329.0 L203.0,324.5 L210.0,320.0 L217.0,315.5 L224.0,311.0 L231.0,306.5 L238.0,302.0 L245.0,297.5 L252.0,293.0 L259.0,288.5 L266.0,284.0 L273.0,279.5 L280.0,275.0 L287.0,270.5 L294.0,266.0 L301.0,261.5 L308.0,257.0 L315.0,252.5 L322.0,248.0 L329.0,243.5 L336.0,239.0 L343.0,234.5 L350.0,230.0 L357.0,225.5 L364.0,221.0 L371.0,216.5 L378.0,212.0 L385.0,207.5 L392.0,203.0 L399.0,198.5 L406.0,194.0 L413.0,189.5 L420.0,185.0 L427.0,180.5 L434.0,176.0 L441.0,171.5 L448.0,167.0 L455.0,162.5 L462.0,158.0 L469.0,153.5 L476.0,149.0 L483.0,144.5 L490.0,140.0" fill="none" stroke="#64748b" stroke-width="2" stroke-dasharray="5 4"/>
<line x1="112.0" y1="140" x2="112.0" y2="410" stroke="#e2e8f0" stroke-width="1.3" stroke-dasharray="3 4"/>
<line x1="280.0" y1="140" x2="280.0" y2="410" stroke="#e2e8f0" stroke-width="1.3" stroke-dasharray="3 4"/>
<line x1="448.0" y1="140" x2="448.0" y2="410" stroke="#e2e8f0" stroke-width="1.3" stroke-dasharray="3 4"/>
<text x="112.0" y="426" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">暗部</text>
<text x="280.0" y="426" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">中間</text>
<text x="448.0" y="426" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明部</text>
<path d="M70.0,383.0 L77.0,378.95 L84.0,374.9 L91.0,370.85 L98.0,366.8 L105.0,362.75 L112.0,358.7 L119.0,354.65 L126.0,350.6 L133.0,346.55 L140.0,342.5 L147.0,338.45 L154.0,334.4 L161.0,330.35 L168.0,326.3 L175.0,322.25 L182.0,318.2 L189.0,314.15 L196.0,310.1 L203.0,306.05 L210.0,302.0 L217.0,297.95 L224.0,293.9 L231.0,289.85 L238.0,285.8 L245.0,281.75 L252.0,277.7 L259.0,273.65 L266.0,269.6 L273.0,265.55 L280.0,261.5 L287.0,257.45 L294.0,253.4 L301.0,249.35 L308.0,245.3 L315.0,241.25 L322.0,237.2 L329.0,233.15 L336.0,229.1 L343.0,225.05 L350.0,221.0 L357.0,216.95 L364.0,212.9 L371.0,208.85 L378.0,204.8 L385.0,200.75 L392.0,196.7 L399.0,192.65 L406.0,188.6 L413.0,184.55 L420.0,180.5 L427.0,176.45 L434.0,172.4 L441.0,168.35 L448.0,164.3 L455.0,160.25 L462.0,156.2 L469.0,152.15 L476.0,148.1 L483.0,144.05 L490.0,140.0" fill="none" stroke="#2563eb" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/></path>
<path d="M70.0,410.0 L77.0,392.38 L84.0,382.03 L91.0,373.36 L98.0,365.61 L105.0,358.49 L112.0,351.83 L119.0,345.53 L126.0,339.53 L133.0,333.78 L140.0,328.23 L147.0,322.87 L154.0,317.66 L161.0,312.6 L168.0,307.67 L175.0,302.85 L182.0,298.14 L189.0,293.53 L196.0,289.0 L203.0,284.56 L210.0,280.2 L217.0,275.91 L224.0,271.68 L231.0,267.52 L238.0,263.42 L245.0,259.38 L252.0,255.39 L259.0,251.45 L266.0,247.56 L273.0,243.71 L280.0,239.91 L287.0,236.15 L294.0,232.43 L301.0,228.75 L308.0,225.11 L315.0,221.5 L322.0,217.93 L329.0,214.39 L336.0,210.88 L343.0,207.4 L350.0,203.95 L357.0,200.53 L364.0,197.14 L371.0,193.77 L378.0,190.43 L385.0,187.12 L392.0,183.83 L399.0,180.56 L406.0,177.32 L413.0,174.1 L420.0,170.9 L427.0,167.72 L434.0,164.57 L441.0,161.43 L448.0,158.31 L455.0,155.22 L462.0,152.14 L469.0,149.08 L476.0,146.03 L483.0,143.01 L490.0,140.0" fill="none" stroke="#2ea043" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2798;0.2800;1.0000" values="0;0;1;1"/></path>
<path d="M70.0,410.0 L77.0,406.4 L84.0,402.8 L91.0,399.2 L98.0,395.6 L105.0,392.0 L112.0,388.4 L119.0,384.8 L126.0,381.2 L133.0,377.6 L140.0,374.0 L147.0,370.4 L154.0,366.8 L161.0,363.2 L168.0,359.6 L175.0,356.0 L182.0,352.4 L189.0,348.8 L196.0,345.2 L203.0,341.6 L210.0,338.0 L217.0,334.4 L224.0,330.8 L231.0,327.2 L238.0,323.6 L245.0,320.0 L252.0,316.4 L259.0,312.8 L266.0,309.2 L273.0,305.6 L280.0,302.0 L287.0,298.4 L294.0,294.8 L301.0,291.2 L308.0,287.6 L315.0,284.0 L322.0,280.4 L329.0,276.8 L336.0,273.2 L343.0,269.6 L350.0,266.0 L357.0,262.4 L364.0,258.8 L371.0,255.2 L378.0,251.6 L385.0,248.0 L392.0,244.4 L399.0,240.8 L406.0,237.2 L413.0,233.6 L420.0,230.0 L427.0,226.4 L434.0,222.8 L441.0,219.2 L448.0,215.6 L455.0,212.0 L462.0,208.4 L469.0,204.8 L476.0,201.2 L483.0,197.6 L490.0,194.0" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4932;0.4933;1.0000" values="0;0;1;1"/></path>
<rect x="540" y="96" width="390" height="340" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="540" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">それぞれが動かした量(出力 − 入力)</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0887;0.0889;1.0000" values="0;0;1;1"/><text x="560" y="134" text-anchor="start" style="font-size:16px;font-weight:700;fill:#2563eb">リフト +0.1</text>
<rect x="680" y="146" width="57.6" height="14" fill="#2563eb" opacity="0.85"/>
<text x="566" y="158" text-anchor="start" style="font-size:11px;font-weight:500;fill:#1f2937">暗部(0.1)</text>
<text x="743.6" y="158" text-anchor="start" style="font-size:11px;font-weight:700;fill:#2563eb">+0.090</text>
<rect x="680" y="166" width="32.0" height="14" fill="#2563eb" opacity="0.85"/>
<text x="566" y="178" text-anchor="start" style="font-size:11px;font-weight:500;fill:#1f2937">中間(0.5)</text>
<text x="718.0" y="178" text-anchor="start" style="font-size:11px;font-weight:700;fill:#2563eb">+0.050</text>
<rect x="680" y="186" width="6.4" height="14" fill="#2563eb" opacity="0.85"/>
<text x="566" y="198" text-anchor="start" style="font-size:11px;font-weight:500;fill:#1f2937">明部(0.9)</text>
<text x="692.4" y="198" text-anchor="start" style="font-size:11px;font-weight:700;fill:#2563eb">+0.010</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3020;0.3022;1.0000" values="0;0;1;1"/><text x="560" y="234" text-anchor="start" style="font-size:16px;font-weight:700;fill:#2ea043">ガンマ 1.5</text>
<rect x="680" y="246" width="73.88" height="14" fill="#2ea043" opacity="0.85"/>
<text x="566" y="258" text-anchor="start" style="font-size:11px;font-weight:500;fill:#1f2937">暗部(0.1)</text>
<text x="759.8838201620406" y="258" text-anchor="start" style="font-size:11px;font-weight:700;fill:#2ea043">+0.115</text>
<rect x="680" y="266" width="83.17" height="14" fill="#2ea043" opacity="0.85"/>
<text x="566" y="278" text-anchor="start" style="font-size:11px;font-weight:500;fill:#1f2937">中間(0.5)</text>
<text x="769.1747359663594" y="278" text-anchor="start" style="font-size:11px;font-weight:700;fill:#2ea043">+0.130</text>
<rect x="680" y="286" width="20.59" height="14" fill="#2ea043" opacity="0.85"/>
<text x="566" y="298" text-anchor="start" style="font-size:11px;font-weight:500;fill:#1f2937">明部(0.9)</text>
<text x="706.5886411431409" y="298" text-anchor="start" style="font-size:11px;font-weight:700;fill:#2ea043">+0.032</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5154;0.5156;1.0000" values="0;0;1;1"/><text x="560" y="334" text-anchor="start" style="font-size:16px;font-weight:700;fill:#e5484d">ゲイン 0.8</text>
<rect x="680" y="346" width="12.8" height="14" fill="#94a3b8" opacity="0.85"/>
<text x="566" y="358" text-anchor="start" style="font-size:11px;font-weight:500;fill:#1f2937">暗部(0.1)</text>
<text x="698.8" y="358" text-anchor="start" style="font-size:11px;font-weight:700;fill:#e5484d">-0.020</text>
<rect x="680" y="366" width="64.0" height="14" fill="#94a3b8" opacity="0.85"/>
<text x="566" y="378" text-anchor="start" style="font-size:11px;font-weight:500;fill:#1f2937">中間(0.5)</text>
<text x="750.0" y="378" text-anchor="start" style="font-size:11px;font-weight:700;fill:#e5484d">-0.100</text>
<rect x="680" y="386" width="115.2" height="14" fill="#94a3b8" opacity="0.85"/>
<text x="566" y="398" text-anchor="start" style="font-size:11px;font-weight:500;fill:#1f2937">明部(0.9)</text>
<text x="801.1999999999999" y="398" text-anchor="start" style="font-size:11px;font-weight:700;fill:#e5484d">-0.180</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6932;0.6933;1.0000" values="0;0;1;1"/><rect x="40" y="452" width="880" height="60" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="56" y="476" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">リフトは暗部を、ガンマは中間を、ゲインは明部を、いちばん動かす。互いに、他をあまり動かさない</text>
<text x="56" y="499" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">3 つのつまみで、「暗部を青く、明部を橙に」といった、色の演出が作れる(RGB それぞれに設定)</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">明るさを、全体で、一括して動かすのではなく、明るさの範囲ごとに動かす<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">3 つのつまみは、効く範囲が違う<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.7065;0.7067;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">色ごとにつまみを持たせると、色味のグレーディングになる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7065;0.7067;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:color-lgg-curves:end -->

## 使いどころ

| ルック | 設定の例 |
| --- | --- |
| 夜・冷たい | リフトに青、ゲインを少し下げる |
| 夕暮れ・暖かい | ゲインにオレンジ |
| 荒廃・色あせ | リフトを持ち上げる（黒が浮く）、彩度を下げる |
| <strong>映画的（ティール＆オレンジ）</strong> | 暗部に青緑、明部にオレンジ |
| コントラストの強い劇画風 | ゲインを上げ、リフトを下げ、ガンマを調整 |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| ガンマ・対数空間で | 映像ツールと感覚が合う |
| CDL 形式でやり取り | 外部のカラリストと数値を共有 |
| LUT に焼く | LGG・バランス・彩度を、1 つの 3D LUT に（[3D LUT](lut-3d.md)） |
| 小さな値で調整 | リフト・カラー バランスは、± 0.05 程度 |
| ボリュームで補間 | 場所ごとに、LGG を補間（[Authoring LUTs](lut-authoring.md)） |

## よくあるミス

??? failure "リフトを上げたら、白まで動いて、全体が白っぽい"
    <strong>リフトの式を、`c + lift · (1 − c)` に</strong>（白を動かさない）。

??? failure "ガンマの向き（`gamma` か `1 / gamma`）を間違えて、逆に動く"
    <strong>`pow(c, 1 / gamma)` で、`gamma > 1` が明るく</strong>。<strong>ツールの定義を確認</strong>。

??? failure "領域ごとのカラー バランスが強すぎて、肌が不自然"
    <strong>小さな値（± 0.05）</strong>、<strong>肌のハイライトを避ける</strong>。

??? failure "リニア空間で LGG を掛けて、効き方がおかしい"
    <strong>ガンマ・対数空間で行う</strong>、またはツールと同じ空間にそろえる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>ゲイン（掛ける・明部）・リフト（足す・暗部）・ガンマ（べき乗・中間）</strong>
    - [x] <strong>RGB 別々に</strong>で<strong>領域ごとの色味づけ</strong>
    - [x] <strong>ASC CDL（スロープ・オフセット・パワー）</strong>は<strong>業界標準</strong>
    - [x] <strong>カラー バランス（シャドウ/ミッド/ハイライト）</strong>は<strong>輝度で重み</strong>
    - [x] <strong>LUT に焼く</strong>。<strong>ガンマ・対数空間で調整</strong>

## 参考

- American Society of Cinematographers, "ASC CDL"
- Selan, "Cinematic Color: From Your Monitor to the Big Screen"（SIGGRAPH 2012）
- Blackmagic Design, "DaVinci Resolve: Primary Color Correction"

## 関連ページ

- [Color Grading](index.md)
- [Basic Adjustments](basic-adjustments.md)
- [White Balance](white-balance.md)
- [3D LUT](lut-3d.md)
