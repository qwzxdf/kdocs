---
title: Reinhard
tags:
  - 描画
---

# Reinhard

<strong>Reinhard</strong> は、もっとも簡単なトーンマップです。式は `x / (1 + x)` だけでどれだけ明るい値も、1 を超えずに 0〜1 に収まります。実装が 1 行で済むので最初の一歩に向きますが、中間調まで圧縮されて、絵が眠くなりやすいので、見た目の目標が決まったら、フィルミックなどに替えます。このページでは、式の性質・白点付きの拡張・チャンネルごとと輝度ベース・改良（より良いやり方）を説明します。

!!! tip "ポイント"
    - 式 ＝ <strong>`c = x / (1 + x)`</strong>。<strong>どれだけ明るくても 1 に漸近</strong>（飽和しない）。
    - x = 1 で 0.5。中間調が持ち上がり、コントラストが低い。
    - 拡張版は白点 L_wを決め、そこでちょうど 1。簡単で見た目が良くなる。
    - 輝度にだけ掛けると色相を保てるが、鮮やかな明部が飽和しすぎることがある。
    - より良いやり方：白点付き ＋ 輝度ベースで色を保つ ＋ 軽いコントラストの調整。

!!! info "このページを読む前に"
    - [Tone Mapping and Exposure](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 式と形

<div class="formula">c = x / (1 + x)</div>

```hlsl
float3 Reinhard(float3 x) {
  return x / (1.0 + x);
}
```

| 入力 x | 出力 c |
| --- | --- |
| 0 | 0 |
| 0.5 | 0.33 |
| 1 | 0.50 |
| 2 | 0.67 |
| 8 | 0.89 |
| 100 | 0.99 |

<strong>x が大きくなるほど増え方が緩やか</strong>になり、1 に近づきます。どんな明るさでも 1 を超えないので、明部が真っ白に潰れる（クランプ）ことはありません。

<!-- fig:tonemap-reinhard:begin -->

<svg class="fig illust motion" data-fig="tonemap-reinhard" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-tonemap-reinhard" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">Reinhard: x ÷ (1 + x)。どんなに明るくても 1 を超えないが、白に届かない。白点を足して、直す</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">明るさ 0 〜 8 の階調。素の Reinhard と、白点つき(L_white)を比べる。L_white を 2 → 4 → 8 に変える</text>
<rect x="30" y="96" width="600" height="270" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 曲線</text>
<path d="M70.0,346.0 L76.75,324.0 L83.5,302.0 L90.25,280.0 L97.0,258.0 L103.75,236.0 L110.5,214.0 L117.25,192.0 L124.0,170.0 L130.75,148.0 L137.5,126.0 L144.25,126.0 L151.0,126.0 L157.75,126.0 L164.5,126.0 L171.25,126.0 L178.0,126.0 L184.75,126.0 L191.5,126.0 L198.25,126.0 L205.0,126.0 L211.75,126.0 L218.5,126.0 L225.25,126.0 L232.0,126.0 L238.75,126.0 L245.5,126.0 L252.25,126.0 L259.0,126.0 L265.75,126.0 L272.5,126.0 L279.25,126.0 L286.0,126.0 L292.75,126.0 L299.5,126.0 L306.25,126.0 L313.0,126.0 L319.75,126.0 L326.5,126.0 L333.25,126.0 L340.0,126.0 L346.75,126.0 L353.5,126.0 L360.25,126.0 L367.0,126.0 L373.75,126.0 L380.5,126.0 L387.25,126.0 L394.0,126.0 L400.75,126.0 L407.5,126.0 L414.25,126.0 L421.0,126.0 L427.75,126.0 L434.5,126.0 L441.25,126.0 L448.0,126.0 L454.75,126.0 L461.5,126.0 L468.25,126.0 L475.0,126.0 L481.75,126.0 L488.5,126.0 L495.25,126.0 L502.0,126.0 L508.75,126.0 L515.5,126.0 L522.25,126.0 L529.0,126.0 L535.75,126.0 L542.5,126.0 L549.25,126.0 L556.0,126.0 L562.75,126.0 L569.5,126.0 L576.25,126.0 L583.0,126.0 L589.75,126.0 L596.5,126.0 L603.25,126.0 L610.0,126.0" fill="none" stroke="#64748b" stroke-width="2" stroke-dasharray="5 4"/>
<path d="M70.0,346.0 L76.75,326.0 L83.5,309.33 L90.25,295.23 L97.0,283.14 L103.75,272.67 L110.5,263.5 L117.25,255.41 L124.0,248.22 L130.75,241.79 L137.5,236.0 L144.25,230.76 L151.0,226.0 L157.75,221.65 L164.5,217.67 L171.25,214.0 L178.0,210.62 L184.75,207.48 L191.5,204.57 L198.25,201.86 L205.0,199.33 L211.75,196.97 L218.5,194.75 L225.25,192.67 L232.0,190.71 L238.75,188.86 L245.5,187.11 L252.25,185.46 L259.0,183.89 L265.75,182.41 L272.5,181.0 L279.25,179.66 L286.0,178.38 L292.75,177.16 L299.5,176.0 L306.25,174.89 L313.0,173.83 L319.75,172.81 L326.5,171.83 L333.25,170.9 L340.0,170.0 L346.75,169.14 L353.5,168.31 L360.25,167.51 L367.0,166.74 L373.75,166.0 L380.5,165.29 L387.25,164.6 L394.0,163.93 L400.75,163.29 L407.5,162.67 L414.25,162.07 L421.0,161.48 L427.75,160.92 L434.5,160.38 L441.25,159.85 L448.0,159.33 L454.75,158.84 L461.5,158.35 L468.25,157.88 L475.0,157.43 L481.75,156.99 L488.5,156.56 L495.25,156.14 L502.0,155.73 L508.75,155.33 L515.5,154.95 L522.25,154.57 L529.0,154.21 L535.75,153.85 L542.5,153.5 L549.25,153.16 L556.0,152.83 L562.75,152.51 L569.5,152.19 L576.25,151.88 L583.0,151.58 L589.75,151.29 L596.5,151.0 L603.25,150.72 L610.0,150.44" fill="none" stroke="#2563eb" stroke-width="3.5"/>
<path d="M70.0,346.0 L76.75,325.5 L83.5,307.5 L90.25,291.42 L97.0,276.86 L103.75,263.5 L110.5,251.12 L117.25,239.56 L124.0,228.67 L130.75,218.34 L137.5,208.5 L144.25,199.07 L151.0,190.0 L157.75,181.24 L164.5,172.75 L171.25,164.5 L178.0,156.46 L184.75,148.61 L191.5,140.93 L198.25,133.4 L205.0,126.0 L211.75,126.0 L218.5,126.0 L225.25,126.0 L232.0,126.0 L238.75,126.0 L245.5,126.0 L252.25,126.0 L259.0,126.0 L265.75,126.0 L272.5,126.0 L279.25,126.0 L286.0,126.0 L292.75,126.0 L299.5,126.0 L306.25,126.0 L313.0,126.0 L319.75,126.0 L326.5,126.0 L333.25,126.0 L340.0,126.0 L346.75,126.0 L353.5,126.0 L360.25,126.0 L367.0,126.0 L373.75,126.0 L380.5,126.0 L387.25,126.0 L394.0,126.0 L400.75,126.0 L407.5,126.0 L414.25,126.0 L421.0,126.0 L427.75,126.0 L434.5,126.0 L441.25,126.0 L448.0,126.0 L454.75,126.0 L461.5,126.0 L468.25,126.0 L475.0,126.0 L481.75,126.0 L488.5,126.0 L495.25,126.0 L502.0,126.0 L508.75,126.0 L515.5,126.0 L522.25,126.0 L529.0,126.0 L535.75,126.0 L542.5,126.0 L549.25,126.0 L556.0,126.0 L562.75,126.0 L569.5,126.0 L576.25,126.0 L583.0,126.0 L589.75,126.0 L596.5,126.0 L603.25,126.0 L610.0,126.0" fill="none" stroke="#e5484d" stroke-width="4"><animate attributeName="d" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698;0.3023;0.5349" values="M70.0,346.0 L76.75,325.5 L83.5,307.5 L90.25,291.42 L97.0,276.86 L103.75,263.5 L110.5,251.12 L117.25,239.56 L124.0,228.67 L130.75,218.34 L137.5,208.5 L144.25,199.07 L151.0,190.0 L157.75,181.24 L164.5,172.75 L171.25,164.5 L178.0,156.46 L184.75,148.61 L191.5,140.93 L198.25,133.4 L205.0,126.0 L211.75,126.0 L218.5,126.0 L225.25,126.0 L232.0,126.0 L238.75,126.0 L245.5,126.0 L252.25,126.0 L259.0,126.0 L265.75,126.0 L272.5,126.0 L279.25,126.0 L286.0,126.0 L292.75,126.0 L299.5,126.0 L306.25,126.0 L313.0,126.0 L319.75,126.0 L326.5,126.0 L333.25,126.0 L340.0,126.0 L346.75,126.0 L353.5,126.0 L360.25,126.0 L367.0,126.0 L373.75,126.0 L380.5,126.0 L387.25,126.0 L394.0,126.0 L400.75,126.0 L407.5,126.0 L414.25,126.0 L421.0,126.0 L427.75,126.0 L434.5,126.0 L441.25,126.0 L448.0,126.0 L454.75,126.0 L461.5,126.0 L468.25,126.0 L475.0,126.0 L481.75,126.0 L488.5,126.0 L495.25,126.0 L502.0,126.0 L508.75,126.0 L515.5,126.0 L522.25,126.0 L529.0,126.0 L535.75,126.0 L542.5,126.0 L549.25,126.0 L556.0,126.0 L562.75,126.0 L569.5,126.0 L576.25,126.0 L583.0,126.0 L589.75,126.0 L596.5,126.0 L603.25,126.0 L610.0,126.0;M70.0,346.0 L76.75,325.5 L83.5,307.5 L90.25,291.42 L97.0,276.86 L103.75,263.5 L110.5,251.12 L117.25,239.56 L124.0,228.67 L130.75,218.34 L137.5,208.5 L144.25,199.07 L151.0,190.0 L157.75,181.24 L164.5,172.75 L171.25,164.5 L178.0,156.46 L184.75,148.61 L191.5,140.93 L198.25,133.4 L205.0,126.0 L211.75,126.0 L218.5,126.0 L225.25,126.0 L232.0,126.0 L238.75,126.0 L245.5,126.0 L252.25,126.0 L259.0,126.0 L265.75,126.0 L272.5,126.0 L279.25,126.0 L286.0,126.0 L292.75,126.0 L299.5,126.0 L306.25,126.0 L313.0,126.0 L319.75,126.0 L326.5,126.0 L333.25,126.0 L340.0,126.0 L346.75,126.0 L353.5,126.0 L360.25,126.0 L367.0,126.0 L373.75,126.0 L380.5,126.0 L387.25,126.0 L394.0,126.0 L400.75,126.0 L407.5,126.0 L414.25,126.0 L421.0,126.0 L427.75,126.0 L434.5,126.0 L441.25,126.0 L448.0,126.0 L454.75,126.0 L461.5,126.0 L468.25,126.0 L475.0,126.0 L481.75,126.0 L488.5,126.0 L495.25,126.0 L502.0,126.0 L508.75,126.0 L515.5,126.0 L522.25,126.0 L529.0,126.0 L535.75,126.0 L542.5,126.0 L549.25,126.0 L556.0,126.0 L562.75,126.0 L569.5,126.0 L576.25,126.0 L583.0,126.0 L589.75,126.0 L596.5,126.0 L603.25,126.0 L610.0,126.0;M70.0,346.0 L76.75,325.88 L83.5,308.88 L90.25,294.28 L97.0,281.57 L103.75,270.38 L110.5,260.41 L117.25,251.45 L124.0,243.33 L130.75,235.93 L137.5,229.12 L144.25,222.84 L151.0,217.0 L157.75,211.55 L164.5,206.44 L171.25,201.62 L178.0,197.08 L184.75,192.76 L191.5,188.66 L198.25,184.75 L205.0,181.0 L211.75,177.41 L218.5,173.95 L225.25,170.62 L232.0,167.41 L238.75,164.3 L245.5,161.29 L252.25,158.37 L259.0,155.53 L265.75,152.76 L272.5,150.06 L279.25,147.43 L286.0,144.86 L292.75,142.34 L299.5,139.88 L306.25,137.46 L313.0,135.09 L319.75,132.76 L326.5,130.47 L333.25,128.22 L340.0,126.0 L346.75,126.0 L353.5,126.0 L360.25,126.0 L367.0,126.0 L373.75,126.0 L380.5,126.0 L387.25,126.0 L394.0,126.0 L400.75,126.0 L407.5,126.0 L414.25,126.0 L421.0,126.0 L427.75,126.0 L434.5,126.0 L441.25,126.0 L448.0,126.0 L454.75,126.0 L461.5,126.0 L468.25,126.0 L475.0,126.0 L481.75,126.0 L488.5,126.0 L495.25,126.0 L502.0,126.0 L508.75,126.0 L515.5,126.0 L522.25,126.0 L529.0,126.0 L535.75,126.0 L542.5,126.0 L549.25,126.0 L556.0,126.0 L562.75,126.0 L569.5,126.0 L576.25,126.0 L583.0,126.0 L589.75,126.0 L596.5,126.0 L603.25,126.0 L610.0,126.0;M70.0,346.0 L76.75,325.97 L83.5,309.22 L90.25,294.99 L97.0,282.75 L103.75,272.09 L110.5,262.73 L117.25,254.42 L124.0,247.0 L130.75,240.32 L137.5,234.28 L144.25,228.78 L151.0,223.75 L157.75,219.13 L164.5,214.86 L171.25,210.91 L178.0,207.23 L184.75,203.8 L191.5,200.59 L198.25,197.58 L205.0,194.75 L211.75,192.08 L218.5,189.55 L225.25,187.16 L232.0,184.88 L238.75,182.72 L245.5,180.66 L252.25,178.69 L259.0,176.8 L265.75,175.0 L272.5,173.27 L279.25,171.6 L286.0,170.0 L292.75,168.46 L299.5,166.97 L306.25,165.53 L313.0,164.14 L319.75,162.8 L326.5,161.49 L333.25,160.23 L340.0,159.0 L346.75,157.81 L353.5,156.65 L360.25,155.52 L367.0,154.42 L373.75,153.34 L380.5,152.3 L387.25,151.27 L394.0,150.28 L400.75,149.3 L407.5,148.34 L414.25,147.41 L421.0,146.49 L427.75,145.59 L434.5,144.71 L441.25,143.85 L448.0,143.0 L454.75,142.17 L461.5,141.35 L468.25,140.54 L475.0,139.75 L481.75,138.97 L488.5,138.2 L495.25,137.45 L502.0,136.7 L508.75,135.97 L515.5,135.25 L522.25,134.53 L529.0,133.83 L535.75,133.13 L542.5,132.45 L549.25,131.77 L556.0,131.1 L562.75,130.44 L569.5,129.78 L576.25,129.13 L583.0,128.49 L589.75,127.86 L596.5,127.23 L603.25,126.61 L610.0,126.0"/></path>
<circle cx="86" cy="120" r="6" fill="#64748b"/>
<text x="96" y="124" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">そのまま</text>
<circle cx="157.6" cy="120" r="6" fill="#2563eb"/>
<text x="167.6" y="124" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">素の Reinhard</text>
<circle cx="309.0" cy="120" r="6" fill="#e5484d"/>
<text x="319.0" y="124" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">白点つき</text>
<rect x="660" y="96" width="270" height="270" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="660" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 数字</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3021;0.3023;1.0000" values="1;1;0;0"/><text x="676" y="134" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d">L_white = 2</text>
<text x="676" y="164" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">入力 8 の出力: 1.00</text>
<text x="676" y="188" text-anchor="start" style="font-size:13px;font-weight:500;fill:#2563eb">素の Reinhard では 0.89</text>
<text x="676" y="216" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">入力 2 以上は 1(白)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3021;0.3023;0.5347;0.5349;1.0000" values="0;0;1;1;0;0"/><text x="676" y="134" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d">L_white = 4</text>
<text x="676" y="164" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">入力 8 の出力: 1.00</text>
<text x="676" y="188" text-anchor="start" style="font-size:13px;font-weight:500;fill:#2563eb">素の Reinhard では 0.89</text>
<text x="676" y="216" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">入力 4 以上は 1(白)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5347;0.5349;1.0000" values="0;0;1;1"/><text x="676" y="134" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d">L_white = 8</text>
<text x="676" y="164" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">入力 8 の出力: 1.00</text>
<text x="676" y="188" text-anchor="start" style="font-size:13px;font-weight:500;fill:#2563eb">素の Reinhard では 0.89</text>
<text x="676" y="216" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">入力 8 以上は 1(白)</text>
</g>
<rect x="30" y="386" width="900" height="90" fill="#ffffff" stroke="#2ea043" stroke-width="1.8" rx="6"/>
<text x="30" y="376" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">③ 階調の見え方(入力 0.3 〜 8)</text>
<text x="40" y="422" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">素の Reinhard</text>
<rect x="230.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2093" values="#e5e7eb;#393939"/></rect>
<rect x="252.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2116" values="#e5e7eb;#5d5d5d"/></rect>
<rect x="274.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2140" values="#e5e7eb;#767676"/></rect>
<rect x="296.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2163" values="#e5e7eb;#888888"/></rect>
<rect x="318.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2186" values="#e5e7eb;#969696"/></rect>
<rect x="340.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2209" values="#e5e7eb;#a1a1a1"/></rect>
<rect x="362.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2233" values="#e5e7eb;#aaaaaa"/></rect>
<rect x="384.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2256" values="#e5e7eb;#b1b1b1"/></rect>
<rect x="406.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2279" values="#e5e7eb;#b8b8b8"/></rect>
<rect x="428.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2302" values="#e5e7eb;#bdbdbd"/></rect>
<rect x="450.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2326" values="#e5e7eb;#c1c1c1"/></rect>
<rect x="472.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2349" values="#e5e7eb;#c5c5c5"/></rect>
<rect x="494.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2372" values="#e5e7eb;#c9c9c9"/></rect>
<rect x="516.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2395" values="#e5e7eb;#cccccc"/></rect>
<rect x="538.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2419" values="#e5e7eb;#cfcfcf"/></rect>
<rect x="560.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2442" values="#e5e7eb;#d1d1d1"/></rect>
<rect x="582.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2465" values="#e5e7eb;#d3d3d3"/></rect>
<rect x="604.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2488" values="#e5e7eb;#d5d5d5"/></rect>
<rect x="626.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2512" values="#e5e7eb;#d7d7d7"/></rect>
<rect x="648.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="670.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2558" values="#e5e7eb;#dbdbdb"/></rect>
<rect x="692.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2581" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="714.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2605" values="#e5e7eb;#dddddd"/></rect>
<rect x="736.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2628" values="#e5e7eb;#dfdfdf"/></rect>
<rect x="758.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2651" values="#e5e7eb;#e0e0e0"/></rect>
<rect x="780.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2674" values="#e5e7eb;#e1e1e1"/></rect>
<rect x="802.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#e5e7eb;#e2e2e2"/></rect>
<rect x="824.0" y="408.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2721" values="#e5e7eb;#e3e3e3"/></rect>
<rect x="230" y="408" width="616.0" height="22.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="40" y="456" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">白点つき(L_white = 4)</text>
<rect x="230.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2093" values="#e5e7eb;#3a3a3a"/></rect>
<rect x="252.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2116" values="#e5e7eb;#606060"/></rect>
<rect x="274.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2140" values="#e5e7eb;#7c7c7c"/></rect>
<rect x="296.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2163" values="#e5e7eb;#929292"/></rect>
<rect x="318.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2186" values="#e5e7eb;#a3a3a3"/></rect>
<rect x="340.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2209" values="#e5e7eb;#b2b2b2"/></rect>
<rect x="362.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2233" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="384.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2256" values="#e5e7eb;#cbcbcb"/></rect>
<rect x="406.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2279" values="#e5e7eb;#d5d5d5"/></rect>
<rect x="428.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2302" values="#e5e7eb;#dfdfdf"/></rect>
<rect x="450.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2326" values="#e5e7eb;#e7e7e7"/></rect>
<rect x="472.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2349" values="#e5e7eb;#f0f0f0"/></rect>
<rect x="494.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2372" values="#e5e7eb;#f8f8f8"/></rect>
<rect x="516.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2395" values="#e5e7eb;#ffffff"/></rect>
<rect x="538.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2419" values="#e5e7eb;#ffffff"/></rect>
<rect x="560.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2442" values="#e5e7eb;#ffffff"/></rect>
<rect x="582.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2465" values="#e5e7eb;#ffffff"/></rect>
<rect x="604.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2488" values="#e5e7eb;#ffffff"/></rect>
<rect x="626.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2512" values="#e5e7eb;#ffffff"/></rect>
<rect x="648.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#e5e7eb;#ffffff"/></rect>
<rect x="670.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2558" values="#e5e7eb;#ffffff"/></rect>
<rect x="692.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2581" values="#e5e7eb;#ffffff"/></rect>
<rect x="714.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2605" values="#e5e7eb;#ffffff"/></rect>
<rect x="736.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2628" values="#e5e7eb;#ffffff"/></rect>
<rect x="758.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2651" values="#e5e7eb;#ffffff"/></rect>
<rect x="780.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2674" values="#e5e7eb;#ffffff"/></rect>
<rect x="802.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#e5e7eb;#ffffff"/></rect>
<rect x="824.0" y="442.0" width="22.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2721" values="#e5e7eb;#ffffff"/></rect>
<rect x="230" y="442" width="616.0" height="22.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">素の Reinhard は、どんなに明るくても、白に届かない<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">白点 L_white を決めると、その明るさが、ちょうど白になる<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.7673;0.7674;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">L_white が小さいほど、明るい所が潰れやすい<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7673;0.7674;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:tonemap-reinhard:end -->

### 性質

| 性質 | 内容 |
| --- | --- |
| 単調増加 | 入力が増えれば、出力も必ず増える（階調が逆転しない） |
| 飽和しない | ∞ でも 1 に漸近する（真っ白に張り付かない） |
| 低コントラスト | x=1 で 0.5 に持ち上がり、暗部も中間も圧縮される → 全体が白っぽく、眠い |
| 白に届かない | x がとても大きくても、1 に届かず、「純白」が出ない |


原典は、Reinhard らの "Photographic Tone Reproduction for Digital Images"（SIGGRAPH 2002）です。論文では、写真家が使う「ゾーン システム」の考え方を取り入れ、画像全体の平均輝度（キー値）に基づいて、全体の明るさを揃えてから、`x / (1 + x)` で圧縮する構成が示されています。式が簡単で、1 行で書けるため、現在でも広く使われています。

原典は、Reinhard らの "Photographic Tone Reproduction for Digital Images"（SIGGRAPH 2002）です。論文では、写真家が使う「ゾーン システム」の考え方を取り入れ、画像全体の平均輝度（キー値）に基づいて、全体の明るさを揃えてから、`x / (1 + x)` で圧縮する構成が示されています。式が簡単で、1 行で書けるため、現在でも広く使われています。

## 白点付き Reinhard

<strong>白点 `L_w`</strong>（この入力値でちょうど 1 になる）を決める拡張です。

<div class="formula">c = x · (1 + x / L_w²) / (1 + x)</div>

```hlsl
float3 ReinhardExtended(float3 x, float white_point) {
  float3 numerator = x * (1.0 + x / (white_point * white_point));
  return numerator / (1.0 + x);
}
```

`white_point` の値による見た目です。小さい値（例：2）なら、早く白に届き、明るくコントラストが強くなります。大きい値（例：8）なら、ゆっくり白に近づき、ハイライトに余裕が残ります。∞にすると、元の Reinhard と同じです。

白点を使うと、「真っ白」が出せるので太陽や強い光がちゃんと白く飛びます。

## チャンネルごと・輝度ベース

<strong>R・G・B に別々に掛ける</strong>と彩度の高い明るい色の色相がずれます。輝度にだけ掛けて、色の比率を保つ方法もあります。

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

色の扱いには 2 通りあります。チャンネルごとに適用する方式は、明るい色が白へ向かい、フィルムのような見た目になりますが、色相がずれます（オレンジが黄に）。輝度ベースの方式は、色相が保たれますが、彩度が高い明部が飽和して、色が濃すぎることがあります。

詳しくは[Preserving Hue](hue-preservation.md)で比べます。

## より良いやり方

<strong>Reinhard をそのまま使う</strong>と眠い絵になりがちです。次の工夫で簡単なまま見栄えを上げられます。

| 工夫 | 内容 |
| --- | --- |
| 白点を設定する | `L_w` を 4〜8 程度にして、ハイライトに余裕を持たせつつ、白を出す |
| 暗部を少し締める | トーンマップ後に軽く S 字のコントラスト（`pow(c, 1.1)` など）を掛ける |
| 輝度ベースで色を保つ | 鮮やかな色が白に飛びすぎるのを防ぐ（ただし、飽和に注意） |
| ブレンド | チャンネルごと 50 % ＋ 輝度ベース 50 %（ハイブリッド） |
| 早めに卒業する | 画作りが固まったら、[Filmic (Hable)](filmic-hable.md)・[ACES](aces.md)・[AgX](agx.md) へ |

## 使いどころ

使いどころの目安です。プロトタイプやデバッグ表示には向きます（1 行で済むため）。UI や 2D 寄りの絵にも向きます（コントラストを強く出さないため）。映画のような画作りの本番には不向きです（眠い絵になるため）。

## よくあるミス

??? failure "Reinhard を掛けたら、全体が白っぽく眠い"
    <strong>曲線の性質</strong>。白点を設定し、軽くコントラストを足す、または別の曲線へ。

??? failure "白点を 1 にして、明るい所が飽和しすぎる"
    `white_point` は 1 より十分大きく（4〜8）。1 だとほぼクランプと同じ。

??? failure "輝度ベースで、鮮やかな光が派手すぎる"
    チャンネルごととブレンドする。または彩度を軽く落とす。

??? failure "ガンマ変換の後に Reinhard を掛けて、暗部が潰れる"
    トーンマップはリニアで。sRGB は最後（[Gamma and HDR Output](gamma-srgb.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] Reinhard ＝ <strong>`x / (1 + x)`</strong>。1 行でどんな明るさも 0〜1 に収まる
    - [x] 中間調が持ち上がって低コントラスト。眠い絵になりやすい
    - [x] 白点付きでちゃんと白を出す（4〜8 が目安）
    - [x] 輝度ベースで色相を保つ。ただし飽和に注意
    - [x] 本番の画作りは、フィルミック・ACES・AgX へ

## 参考

- Reinhard et al., "Photographic Tone Reproduction for Digital Images"（SIGGRAPH 2002）
- Reinhard, Stark, Shirley, Ferwerda, "Photographic Tone Reproduction for Images"（同）

## 関連ページ

- [Tone Mapping and Exposure](index.md)
- [Exposure](exposure.md)
- [Filmic (Hable)](filmic-hable.md)
- [Preserving Hue](hue-preservation.md)
