---
title: Fog Equations
tags:
  - 描画
---

# Fog Equations

<strong>距離に応じて物の色をフォグの色に近づけるのが、フォグ</strong>です。減衰の式には線形・指数・指数二乗があります。このページではフォグの式を説明します。

!!! tip "ポイント"
    - 線形：距離に比例して増える。
    - 指数：exp(−密度 × 距離)（物理的、標準）。
    - 指数二乗：近くは澄み、遠くで急に濃くなる。
    - 最終色 ＝ 物の色 × 透過率 ＋ フォグの色 × (1 − 透過率)。

!!! info "このページを読む前に"
    - [Aerial Perspective and Fog](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

<!-- fig:fog-curves:begin -->

<svg class="fig illust motion" data-fig="fog-curves" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-fog-curves" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">フォグの式: 線形・指数・指数の 2 乗。遠くの物がどれだけ残って見えるかが、違う</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">距離 0〜200 m。物の色が残る割合(透過率)を 3 つの式で計算する。密度は、100 m で 5% しか残らないように、そろえる</text>
<rect x="30" y="96" width="640" height="270" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 透過率(1 = くっきり、0 = 霧の色)</text>
<text x="70.0" y="358" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">0 m</text>
<line x1="70.0" y1="120" x2="70.0" y2="340" stroke="#e2e8f0" stroke-width="1"/>
<text x="212.5" y="358" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">50 m</text>
<line x1="212.5" y1="120" x2="212.5" y2="340" stroke="#e2e8f0" stroke-width="1"/>
<text x="355.0" y="358" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">100 m</text>
<line x1="355.0" y1="120" x2="355.0" y2="340" stroke="#e2e8f0" stroke-width="1"/>
<text x="497.5" y="358" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">150 m</text>
<line x1="497.5" y1="120" x2="497.5" y2="340" stroke="#e2e8f0" stroke-width="1"/>
<text x="640.0" y="358" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">200 m</text>
<line x1="640.0" y1="120" x2="640.0" y2="340" stroke="#e2e8f0" stroke-width="1"/>
<path d="M70.0,120.0 L75.7,123.67 L81.4,127.33 L87.1,131.0 L92.8,134.67 L98.5,138.33 L104.2,142.0 L109.9,145.67 L115.6,149.33 L121.3,153.0 L127.0,156.67 L132.7,160.33 L138.4,164.0 L144.1,167.67 L149.8,171.33 L155.5,175.0 L161.2,178.67 L166.9,182.33 L172.6,186.0 L178.3,189.67 L184.0,193.33 L189.7,197.0 L195.4,200.67 L201.1,204.33 L206.8,208.0 L212.5,211.67 L218.2,215.33 L223.9,219.0 L229.6,222.67 L235.3,226.33 L241.0,230.0 L246.7,233.67 L252.4,237.33 L258.1,241.0 L263.8,244.67 L269.5,248.33 L275.2,252.0 L280.9,255.67 L286.6,259.33 L292.3,263.0 L298.0,266.67 L303.7,270.33 L309.4,274.0 L315.1,277.67 L320.8,281.33 L326.5,285.0 L332.2,288.67 L337.9,292.33 L343.6,296.0 L349.3,299.67 L355.0,303.33 L360.7,307.0 L366.4,310.67 L372.1,314.33 L377.8,318.0 L383.5,321.67 L389.2,325.33 L394.9,329.0 L400.6,332.67 L406.3,336.33 L412.0,340.0 L417.7,340.0 L423.4,340.0 L429.1,340.0 L434.8,340.0 L440.5,340.0 L446.2,340.0 L451.9,340.0 L457.6,340.0 L463.3,340.0 L469.0,340.0 L474.7,340.0 L480.4,340.0 L486.1,340.0 L491.8,340.0 L497.5,340.0 L503.2,340.0 L508.9,340.0 L514.6,340.0 L520.3,340.0 L526.0,340.0 L531.7,340.0 L537.4,340.0 L543.1,340.0 L548.8,340.0 L554.5,340.0 L560.2,340.0 L565.9,340.0 L571.6,340.0 L577.3,340.0 L583.0,340.0 L588.7,340.0 L594.4,340.0 L600.1,340.0 L605.8,340.0 L611.5,340.0 L617.2,340.0 L622.9,340.0 L628.6,340.0 L634.3,340.0 L640.0,340.0" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/></path>
<text x="493.5" y="332.0" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5484d" opacity="0">線形(開始 0・終了 120 m)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,120.0 L75.7,132.79 L81.4,144.84 L87.1,156.19 L92.8,166.88 L98.5,176.95 L104.2,186.43 L109.9,195.36 L115.6,203.77 L121.3,211.7 L127.0,219.16 L132.7,226.19 L138.4,232.8 L144.1,239.04 L149.8,244.91 L155.5,250.44 L161.2,255.65 L166.9,260.55 L172.6,265.17 L178.3,269.53 L184.0,273.62 L189.7,277.48 L195.4,281.12 L201.1,284.54 L206.8,287.77 L212.5,290.81 L218.2,293.67 L223.9,296.36 L229.6,298.9 L235.3,301.29 L241.0,303.54 L246.7,305.66 L252.4,307.66 L258.1,309.54 L263.8,311.31 L269.5,312.98 L275.2,314.55 L280.9,316.03 L286.6,317.42 L292.3,318.74 L298.0,319.97 L303.7,321.14 L309.4,322.24 L315.1,323.27 L320.8,324.24 L326.5,325.16 L332.2,326.02 L337.9,326.83 L343.6,327.6 L349.3,328.32 L355.0,329.0 L360.7,329.64 L366.4,330.24 L372.1,330.81 L377.8,331.34 L383.5,331.85 L389.2,332.32 L394.9,332.77 L400.6,333.19 L406.3,333.58 L412.0,333.96 L417.7,334.31 L423.4,334.64 L429.1,334.95 L434.8,335.25 L440.5,335.52 L446.2,335.78 L451.9,336.03 L457.6,336.26 L463.3,336.48 L469.0,336.68 L474.7,336.87 L480.4,337.06 L486.1,337.23 L491.8,337.39 L497.5,337.54 L503.2,337.68 L508.9,337.82 L514.6,337.94 L520.3,338.06 L526.0,338.18 L531.7,338.28 L537.4,338.38 L543.1,338.48 L548.8,338.57 L554.5,338.65 L560.2,338.73 L565.9,338.8 L571.6,338.87 L577.3,338.94 L583.0,339.0 L588.7,339.06 L594.4,339.11 L600.1,339.16 L605.8,339.21 L611.5,339.26 L617.2,339.3 L622.9,339.34 L628.6,339.38 L634.3,339.42 L640.0,339.45" fill="none" stroke="#2ea043" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2532;0.2533;1.0000" values="0;0;1;1"/></path>
<text x="493.5" y="329.54032522475023" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2ea043" opacity="0">指数 exp(−k·d)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2532;0.2533;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,120.0 L75.7,120.26 L81.4,121.05 L87.1,122.36 L92.8,124.18 L98.5,126.49 L104.2,129.29 L109.9,132.55 L115.6,136.24 L121.3,140.35 L127.0,144.84 L132.7,149.69 L138.4,154.87 L144.1,160.33 L149.8,166.05 L155.5,171.99 L161.2,178.12 L166.9,184.39 L172.6,190.79 L178.3,197.26 L184.0,203.77 L189.7,210.31 L195.4,216.82 L201.1,223.29 L206.8,229.68 L212.5,235.97 L218.2,242.14 L223.9,248.16 L229.6,254.02 L235.3,259.69 L241.0,265.17 L246.7,270.45 L252.4,275.51 L258.1,280.34 L263.8,284.94 L269.5,289.31 L275.2,293.44 L280.9,297.34 L286.6,301.01 L292.3,304.45 L298.0,307.66 L303.7,310.65 L309.4,313.43 L315.1,316.0 L320.8,318.38 L326.5,320.56 L332.2,322.57 L337.9,324.41 L343.6,326.09 L349.3,327.61 L355.0,329.0 L360.7,330.25 L366.4,331.39 L372.1,332.4 L377.8,333.32 L383.5,334.14 L389.2,334.87 L394.9,335.52 L400.6,336.09 L406.3,336.6 L412.0,337.06 L417.7,337.45 L423.4,337.8 L429.1,338.11 L434.8,338.38 L440.5,338.61 L446.2,338.81 L451.9,338.99 L457.6,339.14 L463.3,339.27 L469.0,339.38 L474.7,339.48 L480.4,339.56 L486.1,339.63 L491.8,339.69 L497.5,339.74 L503.2,339.78 L508.9,339.82 L514.6,339.85 L520.3,339.88 L526.0,339.9 L531.7,339.92 L537.4,339.93 L543.1,339.94 L548.8,339.95 L554.5,339.96 L560.2,339.97 L565.9,339.97 L571.6,339.98 L577.3,339.98 L583.0,339.99 L588.7,339.99 L594.4,339.99 L600.1,339.99 L605.8,339.99 L611.5,340.0 L617.2,340.0 L622.9,340.0 L628.6,340.0 L634.3,340.0 L640.0,340.0" fill="none" stroke="#2563eb" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4398;0.4400;1.0000" values="0;0;1;1"/></path>
<text x="493.5" y="331.7399210575241" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2563eb" opacity="0">指数の 2 乗 exp(−(k·d)²)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4398;0.4400;1.0000" values="0;0;1;1"/></text>
<rect x="690" y="96" width="240" height="270" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="690" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 物の見え方(赤い物)</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0887;0.0889;1.0000" values="0;0;1;1"/><text x="706" y="132" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">線形</text>
<rect x="706" y="140" width="46" height="36" fill="#eb948c" stroke="#94a3b8" stroke-width="1"/>
<text x="729" y="190" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">20m</text>
<rect x="758" y="140" width="46" height="36" fill="#e7b1b0" stroke="#94a3b8" stroke-width="1"/>
<text x="781" y="190" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">50m</text>
<rect x="810" y="140" width="46" height="36" fill="#e2d9dd" stroke="#94a3b8" stroke-width="1"/>
<text x="833" y="190" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">100m</text>
<rect x="862" y="140" width="46" height="36" fill="#e0e6ed" stroke="#94a3b8" stroke-width="1"/>
<text x="885" y="190" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">150m</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2754;0.2756;1.0000" values="0;0;1;1"/><text x="706" y="208" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">指数 exp</text>
<rect x="706" y="216" width="46" height="36" fill="#e7b5b4" stroke="#94a3b8" stroke-width="1"/>
<text x="729" y="266" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">20m</text>
<rect x="758" y="216" width="46" height="36" fill="#e3d4d8" stroke="#94a3b8" stroke-width="1"/>
<text x="781" y="266" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">50m</text>
<rect x="810" y="216" width="46" height="36" fill="#e0e2e8" stroke="#94a3b8" stroke-width="1"/>
<text x="833" y="266" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">100m</text>
<rect x="862" y="216" width="46" height="36" fill="#e0e6ec" stroke="#94a3b8" stroke-width="1"/>
<text x="885" y="266" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">150m</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4620;0.4622;1.0000" values="0;0;1;1"/><text x="706" y="284" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">指数の 2 乗 exp</text>
<rect x="706" y="292" width="46" height="36" fill="#eb8c82" stroke="#94a3b8" stroke-width="1"/>
<text x="729" y="342" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">20m</text>
<rect x="758" y="292" width="46" height="36" fill="#e6bdbd" stroke="#94a3b8" stroke-width="1"/>
<text x="781" y="342" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">50m</text>
<rect x="810" y="292" width="46" height="36" fill="#e0e2e8" stroke="#94a3b8" stroke-width="1"/>
<text x="833" y="342" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">100m</text>
<rect x="862" y="292" width="46" height="36" fill="#e0e6ed" stroke="#94a3b8" stroke-width="1"/>
<text x="885" y="342" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">150m</text>
</g>
<text x="40" y="400" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">距離 150 m の物の、残る割合(%):</text>
<text x="300" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0887;0.0889;1.0000" values="1;1;0;0"/></text>
<text x="300" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0887;0.0889;0.2754;0.2756;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">1<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2754;0.2756;0.4620;0.4622;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4620;0.4622;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6132;0.6133;1.0000" values="0;0;1;1"/><rect x="40" y="432" width="880" height="76" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="56" y="456" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">線形は、終了距離で、完全に霧の色。指数は、遠くでも、少し残る(150 m で 1%)</text>
<text x="56" y="479" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">指数の 2 乗は、近くはくっきり、あるところで、一気に霞む。濃い霧の感じに合う(150 m で 0%)</text>
<text x="56" y="501" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">物理的には、指数(Beer の法則)が基本。ほかは、見た目の調整用</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">距離に応じて、物の色を霧の色へ近づける<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">式によって、遠くの物の残り方が違う<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.6265;0.6267;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">100 m で 5% にそろえても、近くと遠くの見え方が違う<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6265;0.6267;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:fog-curves:end -->

## フォグの式
<strong>光は距離 d を進むと減衰して散乱光と入れ替わります</strong>。物の色 C はフォグの色 F と混ざります。

<div class="formula">C_final = C · T + F · (1 − T)　（T：透過率）</div>

| 種類 | 透過率 T | 特徴 |
| --- | --- | --- |
| 線形 | T = saturate((end − d) / (end − start)) | start までは影響なし、end で完全にフォグ。調整しやすいが物理的ではない |
| 指数 | T = exp(−density · d) | 物理的に自然。遠くが徐々に霞む |
| 指数の 2 乗 | T = exp(−(density · d)²) | 近くはほぼ透明である距離から急に霞む |

```hlsl
float FogTransmittance(float distance_to_pixel) {
  return exp(-fog_density * distance_to_pixel);
}

float3 ApplyFog(float3 color, float distance_to_pixel) {
  float t = FogTransmittance(distance_to_pixel);
  return lerp(fog_color, color, t);
}
```

| 点 | 説明 |
| --- | --- |
| 距離はカメラからの直線距離 | 深度（Z）ではなく、位置の長さを使う（画面の端でも同じ濃さ）。`length(world_position − camera_position)` |
| `density` | 0.001〜0.02 /m 程度。視界 200〜2000 m |
| HDR で適用 | トーンマップの前に掛ける |
| 空にもフォグ | 地平線付近の空の色をフォグの色と一致させる（山が空に溶ける） |

### 深度から距離を求める

フル スクリーン パスで深度バッファから位置を再構築して距離を出します。

```hlsl
float3 world_position = ReconstructWorldPosition(uv, depth);
float distance_to_pixel = length(world_position - camera_position);
```

## 霧を式で書く

<strong>霧</strong>（フォグ）は 遠くの物の色を霧の色へ近づける効果です。距離が遠いほど霧の色に染まります。式の骨格は 1 つです。

```text
最終の色 = 物の色 × 透過率  +  霧の色 × (1 − 透過率)
```

透過率（物の色が どれだけ残るか）の、決め方が方式ごとに違います（[Fog Equations](#) の、上の図）。

## 3 つの透過率の式

### ① 線形フォグ

<strong>開始距離</strong>から 終了距離まで、直線的に霧が濃くなります。

```hlsl
float LinearFog(float distance, float fog_start, float fog_end) {
  return saturate((fog_end - distance) / (fog_end - fog_start));       // 透過率: 開始で 1、終了で 0
}
```

`fog_start` より近くでは 透過率 1（霧なし）、`fog_end` より遠くでは 透過率 0（霧の色だけ）です。最も単純で古い方式ですが物理的には、正しくありません（霧の濃さが直線で、変わることはない）。

### ② 指数フォグ

物理に近い式です。進んだ距離に比例して同じ割合ずつ光が減る（Beer の法則）。

```hlsl
float ExpFog(float distance, float density) {
  return exp(-density * distance);                                     // 透過率
}
```

`density` は 霧の濃さです。距離が 2 倍になると透過率が 2 乗に（0.5 → 0.25）なります。霧の現実の振る舞いに近い標準的な式です。

### ③ 指数の 2 乗フォグ

近くはほぼ霧なし、ある距離から急に濃くなる、濃霧の見た目です。

```hlsl
float Exp2Fog(float distance, float density) {
  float f = density * distance;
  return exp(-f * f);
}
```

`exp(−(d × k)²)` は 近くでほぼ 1（霧がほとんど見えない）で ある距離（`1 / k` くらい）から急に 0 へ落ちます。霧の中に入ったような急な視界の悪化を表現できます。

| 式 | 透過率 | 見た目 | 物理的な、正しさ |
| --- | --- | --- | --- |
| 線形 | 直線で減る | 霧の、開始と終了がはっきり | 正しくない |
| 指数 | `exp(−kd)` | 自然な、霞 | 正しい（Beer の法則） |
| 指数の 2 乗 | `exp(−(kd)²)` | 近くは澄み遠くで急に濃い | 正しくない（見た目の、調整用） |

## 霧の色を適用する

```hlsl
// 物の色に霧をかける（ピクセル シェーダーの最後。距離は、カメラからの、実際の距離）。
float3 ApplyFog(float3 scene_color, float distance) {
  float transmittance = ExpFog(distance, g_fog_density);
  return scene_color * transmittance + g_fog_color * (1.0 - transmittance);
}
```

最初の式をそのままコードにしたものです。`distance` は <strong>カメラからその画素までの、距離</strong>です。深度（視点の奥行き）では視線が斜めの画素で霧が薄くなります（距離が実際より短く測られるため）。視線方向の距離を使います。

```hlsl
// 視線方向の距離: ワールド位置から、カメラまでの、実際の距離。
float distance = length(input.world_position - g_camera_position);
```

## RGB ごとの減衰

<strong>霧の色が青っぽい</strong>（空気遠近法）のは、青い光がよく散るためで RGB ごとに、透過率が違うからです。簡易な霧では 1 つの透過率で、霧の色を混ぜます。物理ベースの方式では RGB ごとに別の、消散係数を持ちます（[Physically Based Aerial Perspective](physical.md)）。

```hlsl
float3 transmittance = exp(-g_extinction_rgb * distance);              // RGB ごとの、透過率
float3 result = scene_color * transmittance + g_inscatter_color * (1.0 - transmittance);
```

赤は遠くまで残り、青は先に霧の色へ染まるので、霞む遠景が青みがかる空気遠近法の効果が出ます。

## 密度の決め方

`density`（`σ`）は <strong>「ここまでの距離で、霧の色に染まりきる」</strong>という、見た目の要求から決められます。

```text
透過率が、ほぼ見えなくなる（5%）距離を D とすると:  exp(−σ D) = 0.05  →  σ = 3.0 / D
```

```hlsl
// 「視界が D メートルで、ほぼ、霧の色になる」から、密度を求める。
float DensityFromVisibility(float visibility_m) { return 3.0 / visibility_m; }
```

| 視界の距離 | 霧の状態 | `σ`（1/m） |
| --- | --- | --- |
| 10 km | 澄んだ昼 | 0.0003 |
| 2 km | 薄い霞 | 0.0015 |
| 500 m | 霧 | 0.006 |
| 100 m | 濃霧 | 0.03 |

ゲームの視界を制御するのに、「見える距離」で指定するほうが、直感的です。

## 注意点

| 項目 | 内容 |
| --- | --- |
| HDR | 霧の色は HDR の値（空の、明るさ）に合わせる。霧の色が暗すぎると遠景が暗く沈み、明るすぎると白く浮く（[Matching Fog Color to the Sky](color-match.md)） |
| 加算ブレンドの物 | 火や光の、パーティクル（加算）は霧で暗くなるが、霧の色を足してはいけない（光の物が霧で白く、浮く）。霧の適用は透過率の掛け算だけに、する |
| 半透明 | 半透明の物にも霧をかける（透過率を掛ける）。かけ忘れると遠くの煙が霧の中で、浮く |
| 空 | 空にも霧をかけるかは、場面による。霧の中では空も霧の色に近づく |

## よくあるミス

??? failure "フォグの境目が急で、不自然"
    <strong>指数フォグ</strong>にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 指数フォグが標準

## 参考

- Beer, "Bestimmung der Absorption des rothen Lichts in farbigen Flüssigkeiten", Annalen der Physik, 1852（吸収の法則）
- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Eurographics Symposium on Rendering 2020)
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）
- Wronski, "Volumetric Fog: Unified Compute Shader Based Solution to Atmospheric Scattering", SIGGRAPH 2014, Advances in Real-Time Rendering in Games

## 関連ページ

- [Aerial Perspective and Fog](index.md)
- [Height Fog](height-fog.md)
