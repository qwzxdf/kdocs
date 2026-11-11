---
title: Soft Particles
tags:
  - 描画
---

# Soft Particles

煙や霧のパーティクルはカメラを向く板（ビルボード）で描きます。この板が地面や壁に刺さると板と地面の交差線がくっきり見えます。煙がふわっと立ちのぼっているはずなのに、地面に紙が刺さっているように見えて、不自然です。

<strong>ソフト パーティクルはシーンの深度を読んで、パーティクルが後ろの物に近いほど透明にします</strong>。交差線が消えて板が地面になめらかに溶け込みます。このページでは問題の見え方、フェードの式、線形の深度で比べる理由、完成形のシェーダー、近すぎる場合、低解像度で描く場合の深度の縮小、落とし穴を説明します。

!!! tip "ポイント"
    - パーティクルの視点深度とその画素の後ろにある物の視点深度の差を求めます。
    - 差が小さい（交差に近い）ほどアルファを弱めます。
    - 深度は非線形の値のままでなく、線形の視点深度に直してから引きます。
    - 深度バッファを読むので、書き込みを無効にした読み取り専用の DSV と SRV を組み合わせます。
    - 加算ブレンドのパーティクルでは、アルファでなく色にフェードを掛けます。

!!! info "このページを読む前に"
    - [Alpha Blending and Sorting](index.md)（このセクション全体の地図と、読む順番）

<!-- fig:soft-particles-depth:begin -->

<svg class="fig illust motion" data-fig="soft-particles-depth" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-soft-particles-depth" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ソフト パーティクル:地面に近い部分ほど、薄くして、交差の線を消す</text>
<rect x="40" y="250" width="700" height="14" fill="#d6c7a1"/>
<polygon points="260,90 300,90 520,250 480,250" fill="#94a3b8" fill-opacity="0.25" stroke="#64748b" stroke-width="2" stroke-dasharray="6 4"/>
<text x="180" y="110" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">パーティクルの板</text>
<text x="40" y="304" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">硬い（そのまま）</text>
<rect x="260.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="265.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="271.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="276.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="282.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="287.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="293.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="298.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="304.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="309.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="315.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="320.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="326.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="331.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="337.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="342.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="348.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="353.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="359.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="364.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="370.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="375.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="381.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="386.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="392.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="397.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="403.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="408.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="414.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="419.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="425.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="430.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="436.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="441.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="447.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="452.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="458.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="463.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="469.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="474.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<text x="40" y="354" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">ソフト（深度差でフェード）</text>
<rect x="260.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="265.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="271.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="276.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="282.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="287.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="293.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="298.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="304.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="309.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="315.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="320.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="326.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="331.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="337.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="342.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="348.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="353.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="359.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="364.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="370.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="375.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="381.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="386.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="392.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="397.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="403.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="408.5" y="360" width="5.6" height="30" fill="#7486a2"/>
<rect x="414.0" y="360" width="5.6" height="30" fill="#7e90a9"/>
<rect x="419.5" y="360" width="5.6" height="30" fill="#8999b0"/>
<rect x="425.0" y="360" width="5.6" height="30" fill="#94a2b8"/>
<rect x="430.5" y="360" width="5.6" height="30" fill="#9fabbf"/>
<rect x="436.0" y="360" width="5.6" height="30" fill="#a9b5c6"/>
<rect x="441.5" y="360" width="5.6" height="30" fill="#b4becd"/>
<rect x="447.0" y="360" width="5.6" height="30" fill="#bfc7d4"/>
<rect x="452.5" y="360" width="5.6" height="30" fill="#c9d1db"/>
<rect x="458.0" y="360" width="5.6" height="30" fill="#d4dae2"/>
<rect x="463.5" y="360" width="5.6" height="30" fill="#dfe3ea"/>
<rect x="469.0" y="360" width="5.6" height="30" fill="#eaecf1"/>
<rect x="474.5" y="360" width="5.6" height="30" fill="#f4f6f8"/>
<text x="260" y="296" text-anchor="start" style="font-size:11px;font-weight:700;fill:#64748b">← 板の上側</text>
<text x="480" y="296" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">地面との交差 →</text>
<rect x="260" y="300" width="5.6" height="100" fill="none" stroke="#e5aa28" stroke-width="2.5"><animate attributeName="x" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0800;0.0976;0.1152;0.1328;0.1504;0.1680;0.1856;0.2032;0.2208;0.2384;0.2560;0.2736;0.2912;0.3088;0.3264;0.3440;0.3616;0.3792;0.3968;0.4144;0.4320;0.4496;0.4672;0.4848;0.5024;0.5200;0.5376;0.5552;0.5728;0.5904;0.6080;0.6256;0.6432;0.6608;0.6784;0.6960;0.7136;0.7312;0.7488;0.7664" values="260;260;265.5;271;276.5;282;287.5;293;298.5;304;309.5;315;320.5;326;331.5;337;342.5;348;353.5;359;364.5;370;375.5;381;386.5;392;397.5;403;408.5;414;419.5;425;430.5;436;441.5;447;452.5;458;463.5;469;474.5"/></rect>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 1.00 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1149;0.1152;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.95 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1149;0.1152;0.1501;0.1504;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.89 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1501;0.1504;0.1853;0.1856;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.84 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1853;0.1856;0.2205;0.2208;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.79 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2205;0.2208;0.2557;0.2560;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.74 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2557;0.2560;0.2909;0.2912;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.68 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2909;0.2912;0.3261;0.3264;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.63 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3261;0.3264;0.3613;0.3616;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.58 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3613;0.3616;0.3965;0.3968;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.53 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3965;0.3968;0.4317;0.4320;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.47 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4317;0.4320;0.4669;0.4672;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.42 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4669;0.4672;0.5021;0.5024;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.37 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5021;0.5024;0.5373;0.5376;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.32 → 不透明度 0.90<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5373;0.5376;0.5725;0.5728;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.26 → 不透明度 0.75<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5725;0.5728;0.6077;0.6080;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.21 → 不透明度 0.60<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6077;0.6080;0.6429;0.6432;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.16 → 不透明度 0.45<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6429;0.6432;0.6781;0.6784;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.11 → 不透明度 0.30<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6781;0.6784;0.7133;0.7136;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.05 → 不透明度 0.15<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7133;0.7136;0.7485;0.7488;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.00 → 不透明度 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7485;0.7488;0.7837;0.7840;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">シーンの深度と、板の深度の差を見て、不透明度を決める<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
<text x="540" y="360" text-anchor="start" style="font-size:12px;font-weight:500;fill:#e5484d">硬い:交差で不透明のまま → 線が見える</text>
<text x="540" y="382" text-anchor="start" style="font-size:12px;font-weight:500;fill:#2ea043">ソフト:交差に向けて 0 → 線が消える</text>
</svg>

<!-- fig:soft-particles-depth:end -->

## 問題: 板が地面に刺さる {#problem}

煙のパーティクルは数百枚の板の重なりです。板が地面や壁と交差するとその線の上下で、色が不連続に変わります。

```text
 煙の板
     ╲
      ╲   ← 板が、地面に刺さっている
 ━━━━━━╲━━━━━ 地面
        ╲
         ← 交差した所に、くっきり線が出る
```

深度テストは板を線の手前だけ描いて、線の向こうを描きません。そのため、半透明の板がそこで突然切れます。

## フェードの式 {#fade}

Lorach（2007）のソフト パーティクルは、パーティクルの深度とその後ろにある物の深度の差が小さい所で、パーティクルをフェードさせます。式は次のとおりです。

```text
アルファ = 元のアルファ × saturate( (シーン深度 − パーティクル深度) / フェード距離 )
```

差が 0（交差している）ならアルファは 0 です。フェード距離の半分なら元のアルファの半分です。フェード距離以上離れていれば、元のままです。フェード距離はパーティクルの大きさの半分くらいが目安で、0.5〜2 m の範囲がよく使われます。大きいほど交差線の手前からゆっくり透明になります。

<svg class="fig flow" viewBox="0 0 720 250" role="img" aria-label="深度の差に対するフェードの曲線。線形と smoothstep"><text x="14" y="22" class="fig-title">深度の差 → フェード量</text>
<line x1="70" y1="200" x2="660" y2="200" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="200" x2="70" y2="50" stroke="currentColor" stroke-width="1.5"/>
<text x="660" y="222" text-anchor="end" style="font-size:12px">シーン深度 − パーティクル深度（メートル）</text><text x="62" y="56" text-anchor="end" style="font-size:12px">1</text><text x="62" y="204" text-anchor="end" style="font-size:12px">0</text>
<text x="70" y="220" text-anchor="middle" style="font-size:12px">0</text><text x="400" y="220" text-anchor="middle" style="font-size:12px">フェード距離</text>
<line x1="400" y1="200" x2="400" y2="50" stroke="#94a3b8" stroke-dasharray="4 4"/><line x1="70" y1="50" x2="660" y2="50" stroke="#94a3b8" stroke-dasharray="4 4"/>
<path d="M70,200 L400,50 L660,50" fill="none" stroke="#4c8bf5" stroke-width="3.5"/><text x="300" y="108" text-anchor="end" style="font-size:12px;fill:#4c8bf5;font-weight:600">線形 saturate(x)</text>
<path d="M70,200 C150,198 230,170 285,128 C330,92 360,56 400,50 L660,50" fill="none" stroke="#e5aa28" stroke-width="3.5"/><text x="440" y="90" style="font-size:12px;fill:#b7791f;font-weight:600">smoothstep（端がなだらか）</text>
<text x="360" y="244" text-anchor="middle" style="font-size:12px">交差線の近くは、smoothstep の方が線が目立たない。線形は、境目に折れ曲がりが見える</text></svg>

線形のフェードは `x = 1` の所で傾きが急に変わって、境目に折れ曲がりが見えることがあります。`smoothstep` で端をなだらかにすると交差線がさらに目立たなくなります。

## 線形の深度で比べる {#linear}

深度バッファの値は非線形です。近くで精度が高く遠くで粗くなります。差を取るときは必ず線形の視点深度に直してから引きます。非線形のまま引くと遠くでフェードが効かなくなったり近くで効きすぎたりします。

透視射影で近い面が `near`、遠い面が `far`、標準の深度（近い面が 0、遠い面が 1）の場合、深度バッファの値 `d` から視点深度への変換は、次のとおりです。

```text
視点深度 = near × far / (far − d × (far − near))
```

数字で確かめます。`near = 0.1`、`far = 1000` の場合、`d = 0.5` は視点深度 `0.1 × 1000 / (1000 − 0.5 × 999.9) = 100 / 500.05 ≒ 0.2` メートルです。深度バッファの値の半分（0.5）が、わずか 0.2 m に対応します。残りの 0.5 が 0.2〜1000 m に割り当てられます。非線形のまま差を取ると遠くでは 0.0001 の差が数十メートルに対応します。

リバース Z（近い面が 1、遠い面が 0）を使うなら式が変わります。`d` を `1 − d` に置き換えて同じ式を使います（プロジェクトの射影行列に合わせます）。

## 完成形のシェーダー {#shader}

深度バッファをシェーダー リソースとして読みます。パーティクルの描画では深度の書き込みを無効にするので、同じ深度バッファを読み取り専用の DSV（深度テスト用）と SRV（シェーダーで読む用）の両方で使えます（[Color by Water Depth](../../water/shading/depth-color.md)）。

まず、定数と変換の関数です。

```hlsl
Texture2D<float4> g_particle_tex : register(t0);
Texture2D<float> g_scene_depth : register(t1);      // 不透明パスの深度（SRV）
SamplerState g_linear_clamp : register(s0);

cbuffer ParticleConstants : register(b0) {
  float4x4 g_view_proj;
  float3 g_camera_right;
  float g_near;              // 例: 0.1
  float3 g_camera_up;
  float g_far;               // 例: 1000
  float g_soft_distance;     // ソフト化の距離（メートル）。例: 1.0
  float g_near_fade_start;   // カメラに近すぎるときのフェード開始（メートル）。例: 0.3
  float g_near_fade_range;   // 例: 0.5
  float g_additive;          // 1 = 加算ブレンド、0 = 通常のアルファ ブレンド
};

// 標準の深度（近い面が 0）を、視点深度（メートル）に直す
float LinearizeDepth(float d) {
  return g_near * g_far / (g_far - d * (g_far - g_near));
}
```

次に、頂点シェーダーです。位置と大きさ色が入力で板をカメラへ向けます。

```hlsl
struct Particle {
  float3 center;
  float radius;              // 板の半径（メートル）
  float4 color;
};
StructuredBuffer<Particle> g_particles : register(t2);

struct PsInput {
  float4 position : SV_Position;
  float2 uv : TEXCOORD0;
  float4 color : COLOR0;
};

PsInput ParticleVS(uint vertex_id : SV_VertexID, uint instance_id : SV_InstanceID) {
  Particle p = g_particles[instance_id];
  float2 corner = float2(vertex_id & 1, vertex_id >> 1) * 2.0 - 1.0;   // -1..1
  float3 world = p.center + (g_camera_right * corner.x + g_camera_up * corner.y) * p.radius;

  PsInput o;
  o.position = mul(float4(world, 1.0), g_view_proj);
  o.uv = corner * 0.5 + 0.5;
  o.color = p.color;
  return o;
}
```

最後に、ピクセル シェーダーです。

```hlsl
float4 ParticlePS(PsInput input) : SV_Target {
  float4 color = g_particle_tex.Sample(g_linear_clamp, input.uv) * input.color;

  // ① 後ろにある物の視点深度。同じ画素の位置を整数で読む（Load は補間しない）
  float scene_depth = LinearizeDepth(g_scene_depth.Load(int3(input.position.xy, 0)));

  // ② このパーティクルの視点深度
  float particle_depth = LinearizeDepth(input.position.z);

  // ③ 差に応じてフェード。smoothstep で端をなだらかに
  float x = saturate((scene_depth - particle_depth) / g_soft_distance);
  float fade = x * x * (3.0 - 2.0 * x);

  // ④ カメラに近すぎるパーティクルもフェードする（画面を覆うのを防ぐ。足した処理）
  float near_fade = saturate((particle_depth - g_near_fade_start) / g_near_fade_range);
  fade *= near_fade;

  // ⑤ 通常のブレンドはアルファに、加算ブレンドは色に掛ける
  if (g_additive > 0.5) {
    color.rgb *= fade;
  } else {
    color.a *= fade;
  }
  return color;
}
```

①の `Load` はサンプラーを使わずに画素の整数座標で読みます。パーティクルの画素と同じ位置の不透明な物の深度が、そのまま取れます。

加算ブレンドではアルファが色の強さを決めないので、アルファに掛けても効きません。色（明るさ）に直接掛けます。

C++ 側は読み取り専用の DSV を作って、SRV と同時にバインドします。

```cpp
// （コンパイルしていない）
D3D11_DEPTH_STENCIL_VIEW_DESC dsv_desc = {};
dsv_desc.Format = DXGI_FORMAT_D32_FLOAT;
dsv_desc.ViewDimension = D3D11_DSV_DIMENSION_TEXTURE2D;
dsv_desc.Flags = D3D11_DSV_READ_ONLY_DEPTH;            // 深度を書かない DSV
device->CreateDepthStencilView(depth_texture.Get(), &dsv_desc, &dsv_readonly);

// 深度テストは使うが書き込まない。深度バッファは SRV としても読む
context->OMSetRenderTargets(1, scene_rtv.GetAddressOf(), dsv_readonly.Get());
context->PSSetShaderResources(1, 1, depth_srv.GetAddressOf());
```

深度のテクスチャは `DXGI_FORMAT_R32_TYPELESS` で作って、DSV を `D32_FLOAT`、SRV を `R32_FLOAT` にします。

## 低解像度で描く場合 {#lowres}

煙のような画面を広く覆うパーティクルは、描画コストが大きいので低解像度（半分か 4 分の 1）で描くことがあります。そのときは、深度も縮小して同じ解像度で読みます。縮小するときは平均ではなく最も近い値を残します。平均すると物の縁で手前と奥の深度が混ざって、ありもしない深度ができるからです。

```hlsl
Texture2D<float> g_full_depth : register(t0);
RWTexture2D<float> g_half_depth : register(u0);

[numthreads(8, 8, 1)]
void DownsampleMinDepthCS(uint3 id : SV_DispatchThreadID) {
  uint2 p = id.xy * 2;                                  // 2×2 の左上
  float d0 = g_full_depth[p];
  float d1 = g_full_depth[p + uint2(1, 0)];
  float d2 = g_full_depth[p + uint2(0, 1)];
  float d3 = g_full_depth[p + uint2(1, 1)];
  // 標準の深度（小さいほど近い）なら、最小値が最も近い面。物の縁でも、手前の面が残る
  g_half_depth[id.xy] = min(min(d0, d1), min(d2, d3));
}
```

最も近い面を残すと手前の物の縁の周りで、パーティクルが少し早く消える（ソフトにしすぎる）傾向があります。逆に最も遠い面を残すと手前の物の縁の周りで、フェードが足りなくなってパーティクルの板が手前の物へ漏れます。通常は、最も近い値の方が目立ちにくいです。

## コストと注意点 {#cost}

ソフト パーティクルは 1 画素あたり深度の読み出しが 1 回増えるだけです。ただし、パーティクルは重なる回数（オーバードロー）が大きいことが多いので、画素数が増えます。たとえば、1920 × 1080 の半分を平均 10 枚の板が覆えば、`1920 × 1080 × 0.5 × 10 ≒ 1000 万回` の深度読み出しです。読む値は 1 つなのでほとんどがキャッシュに乗ります。

- MSAA を使っているなら深度は MSAA の深度です。`Texture2DMS` として `Load` でサンプルを指定して読むかリゾルブした深度を使います。
- 同じ原理は水面と岸の境目にも使えます（[Shore Foam: Depth Difference](../../water/shore-foam/shore-depth.md)）。

!!! note "確かめた範囲"
    HLSL は `fxc` で、`ParticleVS`（`vs_5_0`）、`ParticlePS`（`ps_5_0`）、`DownsampleMinDepthCS`（`cs_5_0`）をコンパイルしてエラーが出ないことを確かめました。C++ はコンパイルしていません。数字は式からの手計算です。GPU での描画は確認していません。

## よくあるミス {#mistakes}

??? failure "煙が地面と交差して、硬い線が出る"
    原因はシーンの深度を考慮せずに板をそのまま描いていることです。ソフト パーティクルにして深度の差でフェードします。

??? failure "遠くで、ソフト化が効かない（硬い線が残る）"
    原因は非線形の深度のまま差を取っていることです。遠くの深度は精度が粗く差がほぼ 0 になります。視点深度に直してから引きます。

??? failure "加算ブレンドの火花が、フェードしても光ったままになる"
    原因はアルファにだけ `fade` を掛けていることです。加算ブレンドでは色そのものが足されるので、アルファを変えても効きません。`color.rgb` に掛けます。

??? failure "ドローコールがエラーになる深度が読めない"
    原因は同じ深度バッファを書き込み可能な DSV と SRV に同時にバインドしていることです。読み取り専用の DSV（`D3D11_DSV_READ_ONLY_DEPTH`）を作ります。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 後ろの物との視点深度の差が小さいほどパーティクルを透明にします。
    - [x] 深度は線形の視点深度に直してから引きます。
    - [x] 加算ブレンドは色にフェードを掛けます。
    - [x] 低解像度で描くときは、深度の縮小に最小値（最も近い面）を使います。

## 参考 {#references}

このページは次の資料を読まずに書きました。フェードの式の形は一般的なもので、`smoothstep` や近すぎるときのフェードは自分で足した処理です。

- Lorach, "Soft Particles", NVIDIA White Paper, 2007
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（透明、屈折、フレネルの章）
- Microsoft Learn, "D3D11_RENDER_TARGET_BLEND_DESC"（`SrcBlend`、`DestBlend`、`BlendOp`）
- Microsoft Learn, "Reading depth-stencil as shader resource"

## 関連ページ

- [Alpha Blending and Sorting](index.md)
- [Sorting](sorting.md)
